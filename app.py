import streamlit as st
import os
import psutil
import pandas as pd

# --- Fungsi Pendukung ---
def get_drive_list():
    drives = []
    for p in psutil.disk_partitions():
        try:
            # Mengambil informasi device saja
            usage = psutil.disk_usage(p.mountpoint)
            drives.append({
                "label": f"Drive {p.mountpoint} ({usage.percent}% Terpakai)",
                "path": p.mountpoint
            })
        except: continue
    return drives

def get_size_format(b):
    for unit in ["", "K", "M", "G", "T"]:
        if b < 1024: return f"{b:.2f}{unit}B"
        b /= 1024
    return f"{b:.2f}TB"

@st.fragment # Optimasi agar hanya bagian ini yang terupdate
def run_scan_logic(path, mode):
    data = []
    files_found = 0
    status_placeholder = st.empty()
    
    for root, dirs, files in os.walk(path):
        for name in files:
            file_path = os.path.join(root, name)
            try:
                size = os.path.getsize(file_path)
                data.append({
                    "Nama File": name,
                    "Ukuran (Bytes)": size,
                    "Format": os.path.splitext(name)[1].lower() or "Lainnya",
                    "Path": file_path
                })
                files_found += 1
                if files_found % 1000 == 0:
                    status_placeholder.text(f"🔍 Memproses... {files_found} file ditemukan")
            except: continue
            
    status_placeholder.empty()
    df = pd.DataFrame(data)
    if mode == "10 Terbesar Saja" and not df.empty:
        return df.nlargest(10, "Ukuran (Bytes)")
    return df

# --- Konfigurasi Halaman ---
st.set_page_config(page_title="Storage Manager", layout="centered")

# Inisialisasi State
if 'scan_data' not in st.session_state:
    st.session_state.scan_data = None

# --- UI UTAMA ---
st.title("🖥️ Manajemen Penyimpanan")
st.write("Pilih hardisk yang ingin Anda kelola di bawah ini.")

# Tampilan Pilihan Drive
drives = get_drive_list()
col1, col2 = st.columns([3, 1])

with col1:
    selected_drive = st.selectbox("Daftar Perangkat Terdeteksi:", drives, format_func=lambda x: x["label"])

with col2:
    scan_mode = st.selectbox("Mode:", ["10 Terbesar Saja", "Full Scan"])

# Logika Pop-up Persetujuan
@st.dialog("Persetujuan Akses Penyimpanan")
def confirm_dialog(path, mode):
    st.warning(f"Anda akan memindai direktori: **{path}**")
    st.write("Aplikasi memerlukan izin untuk membaca metadata file. Beberapa file sistem mungkin tidak dapat diakses tanpa izin Administrator.")
    st.info("Lanjutkan pemindaian?")
    if st.button("Ya, Saya Setuju & Mulai Scan"):
        with st.spinner("Menganalisis..."):
            result = run_scan_logic(path, mode)
            st.session_state.scan_data = result
            st.rerun()

# Tombol Analisis
if st.button("🚀 Analisis Sekarang", use_container_width=True):
    confirm_dialog(selected_drive["path"], scan_mode)

st.divider()

# --- TAMPILAN HASIL (Hanya muncul jika sudah di-scan) ---
if st.session_state.scan_data is not None:
    df = st.session_state.scan_data
    
    if not df.empty:
        st.success(f"Analisis Selesai! Menemukan {len(df)} file.")
        df["Kapasitas"] = df["Ukuran (Bytes)"].apply(get_size_format)
        
        # Tampilkan Tabel
        st.subheader("Detail Penyimpanan")
        st.dataframe(
            df[["Nama File", "Kapasitas", "Format", "Path"]].sort_values("Ukuran (Bytes)", ascending=False),
            use_container_width=True,
            hide_index=True
        )
        
        if st.button("Bersihkan Hasil"):
            st.session_state.scan_data = None
            st.rerun()
    else:
        st.error("Akses ditolak atau drive kosong. Coba jalankan aplikasi sebagai Administrator.")

# Sembunyikan Menu Streamlit (Sesuai preferensi Anda)
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>", unsafe_allow_html=True)
