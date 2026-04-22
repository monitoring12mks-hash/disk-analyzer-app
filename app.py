import streamlit as st
import os
import psutil
import pandas as pd
import time

# --- 1. Fungsi Pendukung ---
def get_drive_list():
    drives = []
    for p in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(p.mountpoint)
            label = f"{p.mountpoint} [Total: {usage.total/(1024**3):.1f} GB | Terpakai: {usage.percent}%]"
            drives.append({"label": label, "path": p.mountpoint})
        except: continue
    return drives

def get_size_format(b):
    for unit in ["", "K", "M", "G", "T"]:
        if b < 1024: return f"{b:.2f}{unit}B"
        b /= 1024
    return f"{b:.2f}TB"

def run_disk_scan(path, mode):
    data = []
    # Placeholder untuk progress agar user tahu app bekerja
    status_text = st.empty()
    files_found = 0
    
    for root, dirs, files in os.walk(path):
        for name in files:
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
                    status_text.text(f"🔍 Menemukan {files_found} file...")
            except: continue
            
    status_text.empty()
    df = pd.DataFrame(data)
    if mode == "10 Terbesar Saja" and not df.empty:
        return df.nlargest(10, "Ukuran (Bytes)")
    return df

# --- 2. Konfigurasi App ---
st.set_page_config(page_title="Storage Manager Pro", layout="wide")

# Inisialisasi Session State agar data tidak hilang saat diklik
if 'scan_results' not in st.session_state:
    st.session_state['scan_results'] = None

# --- 3. Sidebar UI ---
st.sidebar.header("🎛️ Manajemen Storage")
list_drives = get_drive_list()

if list_drives:
    selected_drive = st.sidebar.selectbox(
        "Pilih Hardisk / Devices:", 
        list_drives, 
        format_func=lambda x: x["label"]
    )
    target_path = selected_drive["path"]
else:
    target_path = st.sidebar.text_input("Path Manual:", value="C:/")

scan_mode = st.sidebar.radio("Mode Scan:", ["10 Terbesar Saja", "Full Scan (Semua File)"])

# TOMBOL ANALISIS
if st.sidebar.button("🚀 Mulai Analisis"):
    with st.spinner(f"Sedang memproses {target_path}..."):
        # Jalankan fungsi scan dan simpan ke session state
        df_result = run_disk_scan(target_path, scan_mode)
        st.session_state['scan_results'] = df_result
        st.session_state['last_scan_path'] = target_path

# --- 4. Main Dashboard ---
st.title("🖥️ Disk Device Analyzer")

if st.session_state['scan_results'] is not None:
    df = st.session_state['scan_results']
    
    if not df.empty:
        # Tambahkan kolom bacaan ukuran
        df["Ukuran Detail"] = df["Ukuran (Bytes)"].apply(get_size_format)
        
        # Row Statistik
        c1, c2, c3 = st.columns(3)
        c1.metric("Device", st.session_state['last_scan_path'])
        c2.metric("Total File", len(df))
        c3.metric("Total Kapasitas", get_size_format(df["Ukuran (Bytes)"].sum()))
        
        st.divider()

        # Tampilkan Hasil
        if len(df) <= 10:
            st.subheader("🚨 File Terbesar yang Ditemukan")
            st.table(df[["Nama File", "Ukuran Detail", "Format", "Path"]])
        else:
            st.subheader("📊 Laporan Lengkap")
            st.dataframe(df[["Nama File", "Ukuran Detail", "Format", "Path"]], use_container_width=True)
            
        # Tombol Reset
        if st.button("Clear Results"):
            st.session_state['scan_results'] = None
            st.rerun()
    else:
        st.warning("Tidak ada file yang ditemukan atau akses ditolak oleh sistem.")
else:
    st.info("Pilih drive di sidebar dan klik **Mulai Analisis** untuk melihat detail penyimpanan.")

# --- Styling ---
st.markdown("""
    <style>
    .stMetric { border: 1px solid #eee; padding: 15px; border-radius: 10px; background: #fafafa; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)
