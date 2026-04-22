import streamlit as st
import os
import pandas as pd
import time

# --- Konfigurasi Page ---
st.set_page_config(page_title="Storage Manager Pro", layout="wide")

def get_size_format(b):
    for unit in ["", "K", "M", "G", "T"]:
        if b < 1024: return f"{b:.2f}{unit}B"
        b /= 1024

def scan_storage(path, mode="Full Scan"):
    data = []
    start_time = time.time()
    
    # Progress Bar
    progress_text = "Memulai pemindaian..."
    bar = st.progress(0, text=progress_text)
    
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
                # Update progress setiap 500 file agar tidak lag
                if files_found % 500 == 0:
                    bar.progress(min(files_found / 10000, 0.99), text=f"Menemukan {files_found} file...")
            except (PermissionError, FileNotFoundError):
                continue
    
    df = pd.DataFrame(data)
    bar.empty() # Hapus progress bar jika selesai
    
    if df.empty:
        return df

    # Logika Pilihan User
    if mode == "10 Terbesar Saja":
        return df.nlargest(10, "Ukuran (Bytes)")
    
    return df

# --- UI Sidebar ---
st.sidebar.header("⚙️ Pengaturan Scan")
drive_path = st.sidebar.text_input("Path Hardisk / Folder:", value="C:/" if os.name == 'nt' else "/")
scan_mode = st.sidebar.radio("Mode Manajemen:", ["Full Scan", "10 Terbesar Saja"])
start_btn = st.sidebar.button("Jalankan Pemindaian")

# --- Main UI ---
st.title("🗂️ Storage Management Dashboard")

if start_btn:
    if os.path.exists(drive_path):
        with st.spinner(f"Sedang menganalisis {drive_path}..."):
            results = scan_storage(drive_path, mode=scan_mode)
            
            if not results.empty:
                # Kolom format size agar mudah dibaca
                results["Ukuran Detail"] = results["Ukuran (Bytes)"].apply(get_size_format)
                
                # --- Statistik Ringkasan ---
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total File", len(results))
                with col2:
                    total_size = results["Ukuran (Bytes)"].sum()
                    st.metric("Total Penggunaan", get_size_format(total_size))
                with col3:
                    st.metric("Mode", scan_mode)

                st.divider()

                # --- Tampilan Hasil ---
                if scan_mode == "10 Terbesar Saja":
                    st.subheader("🚨 10 File Terbesar (Penyebab Disk Penuh)")
                    # Highlight khusus untuk file raksasa
                    st.table(results[["Nama File", "Ukuran Detail", "Format", "Path"]])
                
                else:
                    st.subheader("📊 Laporan Lengkap Penyimpanan")
                    tab1, tab2 = st.tabs(["Daftar Semua File", "Berdasarkan Jenis"])
                    
                    with tab1:
                        st.dataframe(results[["Nama File", "Ukuran Detail", "Format", "Path"]].sort_values("Nama File"), use_container_width=True)
                    
                    with tab2:
                        type_analysis = results.groupby("Format").size().reset_index(name="Jumlah")
                        st.bar_chart(type_analysis.set_index("Format"))
                        st.dataframe(type_analysis.sort_values("Jumlah", ascending=False), use_container_width=True)
            else:
                st.error("Tidak dapat membaca data. Pastikan Anda memiliki izin akses pada folder tersebut.")
    else:
        st.error("Path tidak ditemukan. Pastikan format penulisan benar.")
else:
    st.info("Silakan tentukan path hardisk di sidebar dan klik 'Jalankan Pemindaian'.")

# --- Custom Clean UI (Sesuai gaya favorit Anda) ---
st.markdown("""
    <style>
    .stMetric { border: 1px solid #e6e9ef; padding: 15px; border-radius: 5px; background: #ffffff; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)
