import streamlit as st
import os
import pandas as pd
from pathlib import Path

# Konfigurasi Halaman
st.set_page_config(page_title="Disk Analyzer Pro", layout="wide")

def get_size_format(b, factor=1024, suffix="B"):
    """Mengubah bytes menjadi format yang mudah dibaca (KB, MB, GB)"""
    for unit in ["", "K", "M", "G", "T", "P"]:
        if b < factor:
            return f"{b:.2f}{unit}{suffix}"
        b /= factor

def scan_directory(path):
    data = []
    # Menggunakan os.walk untuk menelusuri folder dan subfolder
    for root, dirs, files in os.walk(path):
        for name in files:
            file_path = os.path.join(root, name)
            try:
                # Ambil informasi file
                stats = os.stat(file_path)
                size = stats.st_size
                extension = os.path.splitext(name)[1].lower() or "No Extension"
                
                data.append({
                    "Nama File": name,
                    "Path": file_path,
                    "Ukuran (Bytes)": size,
                    "Format": extension,
                    "Ukuran": get_size_format(size)
                })
            except (PermissionError, FileNotFoundError):
                continue
    return pd.DataFrame(data)

# Antarmuka Pengguna (UI)
st.title("📂 Disk Storage Analyzer")
st.markdown("Analisis file besar di penyimpanan lokal Anda dengan detail.")

# Input Path
target_path = st.text_input("Masukkan Path Folder (Contoh: C:/Users/Documents atau /Users/Name/Downloads):", value=".")

if st.button("Mulai Scanning"):
    if os.path.exists(target_path):
        with st.spinner("Sedang memindai file... Harap tunggu..."):
            df = scan_directory(target_path)
            
            if not df.empty:
                # Sorting berdasarkan ukuran terbesar
                df = df.sort_values(by="Ukuran (Bytes)", ascending=False)

                # Row 1: Ringkasan Statistik
                col1, col2, col3 = st.columns(3)
                col1.metric("Total File", len(df))
                col2.metric("Total Kapasitas", get_size_format(df["Ukuran (Bytes)"].sum()))
                col3.metric("Jenis File Terdeteksi", len(df["Format"].unique()))

                # Row 2: Visualisasi & Detail
                st.divider()
                
                tab1, tab2 = st.tabs(["📊 Daftar File Detail", "📁 Analisis Format"])
                
                with tab1:
                    st.subheader("Daftar File (Besar ke Kecil)")
                    # Tampilkan tabel tanpa kolom bytes mentah agar rapi
                    st.dataframe(df[["Nama File", "Ukuran", "Format", "Path"]], use_container_width=True)

                with tab2:
                    st.subheader("Distribusi Berdasarkan Jenis File")
                    type_summary = df.groupby("Format").agg({
                        "Nama File": "count",
                        "Ukuran (Bytes)": "sum"
                    }).rename(columns={"Nama File": "Jumlah File", "Ukuran (Bytes)": "Total Size (Bytes)"})
                    
                    # Tambahkan kolom size yang mudah dibaca
                    type_summary["Total Kapasitas"] = type_summary["Total Size (Bytes)"].apply(get_size_format)
                    st.table(type_summary[["Jumlah File", "Total Kapasitas"]].sort_values(by="Jumlah File", ascending=False))
            else:
                st.warning("Tidak ada file ditemukan atau akses ditolak.")
    else:
        st.error("Path tidak valid! Pastikan format path benar.")

# CSS Custom untuk mempercantik tampilan
st.markdown("""
    <style>
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)
