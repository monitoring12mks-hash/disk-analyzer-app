import streamlit as st
import os
import pandas as pd
import time
import psutil  # Library baru untuk deteksi drive

# --- Fungsi Pendukung ---
def get_available_drives():
    """Mendeteksi semua drive/partisi yang terpasang di PC"""
    drives = []
    partitions = psutil.disk_partitions()
    for p in partitions:
        # Hanya ambil drive yang siap (bukan CD-ROM kosong)
        if os.name == 'nt': # Windows
            if 'fixed' in p.opts or 'rw' in p.opts:
                drives.append(p.device)
        else: # Mac/Linux
            drives.append(p.mountpoint)
    return drives

def get_size_format(b):
    for unit in ["", "K", "M", "G", "T"]:
        if b < 1024: return f"{b:.2f}{unit}B"
        b /= 1024
    return f"{b:.2f}TB"

# --- Konfigurasi Page ---
st.set_page_config(page_title="Storage Manager Pro", layout="wide")

# --- UI Sidebar ---
st.sidebar.header("⚙️ Pengaturan Scan")

# 1. Pilih Drive Otomatis
available_drives = get_available_drives()
selected_drive = st.sidebar.selectbox("Pilih Hardisk/Drive:", available_drives)

# 2. Pilihan Mode
scan_mode = st.sidebar.radio("Mode Manajemen:", ["Full Scan", "10 Terbesar Saja"])

# 3. Filter Jenis File (Opsional untuk Full Scan Maksimal)
enable_filter = st.sidebar.checkbox("Filter Format Tertentu?")
selected_ext = ""
if enable_filter:
    selected_ext = st.sidebar.text_input("Masukkan Ekstensi (Contoh: .mp4, .zip):")

start_btn = st.sidebar.button("Jalankan Pemindaian")

# --- Logika Scan ---
def scan_storage(path, mode, filter_ext=""):
    data = []
    bar = st.progress(0, text="Menyiapkan data...")
    files_found = 0
    
    for root, dirs, files in os.walk(path):
        for name in files:
            # Jika filter aktif, lewati file yang tidak sesuai
            if filter_ext and not name.lower().endswith(filter_ext.lower()):
                continue
                
            file_path = os.path.join(root, name)
            try:
                size = os.path.getsize(file_path)
                ext = os.path.splitext(name)[1].lower() or "Unknown"
                data.append({
                    "Nama File": name,
                    "Ukuran (Bytes)": size,
                    "Format": ext,
                    "Path": file_path
                })
                files_found += 1
                if files_found % 1000 == 0:
                    bar.progress(0.5, text=f"Menganalisis {files_found} file...")
            except:
                continue
    
    bar.empty()
    df = pd.DataFrame(data)
    if mode == "10 Terbesar Saja" and not df.empty:
        return df.nlargest(10, "Ukuran (Bytes)")
    return df

# --- Main Dashboard ---
st.title("🗂️ Storage Management Dashboard")

if start_btn:
    with st.spinner(f"Memindai {selected_drive}..."):
        results = scan_storage(selected_drive, scan_mode, selected_ext)
        
        if not results.empty:
            results["Ukuran Detail"] = results["Ukuran (Bytes)"].apply(get_size_format)
            
            # Statistik Cepat
            c1, c2, c3 = st.columns(3)
            c1.metric("Drive", selected_drive)
            c2.metric("Total File Terdeteksi", len(results))
            c3.metric("Total Size", get_size_format(results["Ukuran (Bytes)"].sum()))
            
            st.divider()
            
            if scan_mode == "10 Terbesar Saja":
                st.subheader("🚨 File Paling Boros Kapasitas")
                st.table(results[["Nama File", "Ukuran Detail", "Format", "Path"]])
            else:
                st.subheader("📊 Laporan Lengkap")
                st.dataframe(results[["Nama File", "Ukuran Detail", "Format", "Path"]], use_container_width=True)
        else:
            st.warning("Data tidak ditemukan atau izin akses ditolak.")

# CSS Custom
st.markdown("""
    <style>
    .stMetric { border: 1px solid #eee; padding: 10px; border-radius: 10px; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)
