import streamlit as st

# ================== PAGE CONFIG ==================
st.set_page_config(page_title="Tentang Aplikasi", page_icon="ℹ️", layout="wide")
st.header("ℹ️ Tentang Aplikasi")

# ================== DESKRIPSI SINGKAT ==================
st.markdown("""
Aplikasi ini adalah **workshop sederhana** untuk memuat data Excel, melakukan sedikit analisis,
dan menampilkan **visualisasi interaktif** (Line, Bar, Pie, Scatter).

Semua proses dilakukan langsung di browser menggunakan **Streamlit** dan **Plotly**.
""")

# ================== DATASET YANG DIGUNAKAN ==================
with st.expander("📁 Dataset yang Digunakan", expanded=True):
    st.markdown("""
- **Data Nilai Tukar** (mis. DXY / mata uang)  
- **Data Indikator Keuangan** lain yang bersifat numerik (opsional)  
- Format file: **Excel/CSV** dengan **kolom pertama = Tanggal** dan **kolom lain = nilai numerik**.
""")

# ================== STRUKTUR HALAMAN / FILE ==================
with st.expander("🗂️ Struktur Halaman & File (dengan ikon)", expanded=True):
    st.markdown("""
- `Dashboard` *(root app)*
- `pages/1_ℹ️_About.py` – **ℹ️ About**: halaman ini
- `pages/2_📘_Data_Excel.py` – **📘 Data Excel**: unggah file & preview
- `pages/3_🧪_Analisis.py` – **🧪 Analisis**: ringkasan sederhana
- `pages/4_📊_Visualisasi.py` – **📊 Visualisasi**: line/bar/pie/scatter interaktif
- `pages/5_📊_Forecast.py` – **📊 Forecast**: forecasting sederhana
""")

# ================== CARA PAKAI SINGKAT ==================
with st.expander("🧭 Cara Pakai", expanded=True):
    st.markdown("""
1) Buka **📘 Data Excel** → upload file (kolom pertama sebaiknya tanggal).  
2) Masuk ke **📊 Visualisasi** → pilih kolom numerik, atur rentang tanggal, lihat grafik.  
3) (Opsional) **🧪 Analisis** → cek ringkasan/statistik.  
4) Gunakan tombol **Save** (jika ada) untuk unduh grafik sebagai PNG.
""")

# ================== CATATAN / BATASAN ==================
with st.expander("⚠️ Catatan & Batasan", expanded=False):
    st.markdown("""
- Tipe data tanggal harus valid agar filter & grafik waktu berfungsi.
""")


st.caption("© Workshop Streamlit.")
