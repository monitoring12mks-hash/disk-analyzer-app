import streamlit as st
import os
import psutil
import pandas as pd

# --- Fungsi Mendapatkan Detail Drive ---
def get_drive_list():
    """Mendapatkan daftar drive dengan info kapasitas untuk memudahkan pilihan"""
    drives = []
    partitions = psutil.disk_partitions()
    for p in partitions:
        try:
            # Pastikan drive siap (menghindari error pada CD-ROM kosong)
            usage = psutil.disk_usage(p.mountpoint)
            # Format tampilan: "C:/ (Total: 250GB - Terpakai: 80%)"
            total_gb = usage.total / (1024**3)
            percent = usage.percent
            label = f"{p.mountpoint} [Total: {total_gb:.1f} GB | Terpakai: {percent}%]"
            
            drives.append({
                "label": label,
                "path": p.mountpoint
            })
        except:
            continue
    return drives

# --- UI Sidebar ---
st.sidebar.header("🎛️ Manajemen Storage")

# Mengambil data drive/device
list_drives = get_drive_list()
if list_drives:
    # User memilih berdasarkan label, tapi kita ambil path-nya
    drive_options = {d["label"]: d["path"] for d in list_drives}
    selected_label = st.sidebar.selectbox("Pilih Hardisk / Partisi:", list_drives, format_func=lambda x: x["label"])
    target_path = selected_label["path"]
else:
    target_path = st.sidebar.text_input("Path tidak terdeteksi, masukkan manual:", value="C:/")

# Pilihan Mode
scan_mode = st.sidebar.radio("Mode Scan:", ["10 Terbesar Saja", "Full Scan (Semua File)"])

st.sidebar.divider()

# Tombol Eksekusi
if st.sidebar.button("🚀 Mulai Analisis"):
    st.session_state['run_scan'] = True
else:
    if 'run_scan' not in st.session_state:
        st.session_state['run_scan'] = False

# --- Main Logic ---
st.title("🖥️ Disk Device Analyzer")

if st.session_state['run_scan']:
    st.info(f"Menganalisis Device: **{target_path}**")
    
    # (Gunakan fungsi scan_storage dari kode sebelumnya di sini)
    # ...
