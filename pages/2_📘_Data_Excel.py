import streamlit as st
from utils.load_css import load_css
import pandas as pd
from utils.auth import is_logged_in

if not is_logged_in():
    st.warning("⚠️ Silakan login terlebih dahulu di halaman 🔐 Login.")
    st.stop()

#load_css("style.css")
st.header("📘 Pengolahan Data Excel")
st.write("Unggah file Excel untuk dianalisis. Sistem akan menampilkan data, "
         "menentukan tipe data numerik dan kategorikal, serta memberikan ringkasan statistik awal.")

# ========== Bagian Upload ==========
with st.expander("📂 Unggah File Excel", expanded=True):
    uploaded_file = st.file_uploader("Pilih file Excel", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        st.session_state["uploaded_df"] = df
        st.success("✅ File berhasil dibaca!")

        # ========== Bagian DataFrame ==========
        with st.expander("📄 Tampilkan Data", expanded=True):
            st.dataframe(df, use_container_width=True)

        # ========== Bagian Identifikasi Tipe Data ==========
        with st.expander("🔍 Identifikasi Tipe Data"):
            dtypes = df.dtypes.reset_index()
            dtypes.columns = ["Kolom", "Tipe Data"]
            st.table(dtypes)

        # ========== Bagian Klasifikasi Kolom ==========
        with st.expander("🧮 Klasifikasi Kolom Numerik dan Kategorikal"):
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            categorical_cols = df.select_dtypes(exclude=['number']).columns.tolist()

            st.markdown(f"**Kolom Numerik:** {', '.join(numeric_cols) if numeric_cols else 'Tidak ada'}")
            st.markdown(f"**Kolom Kategorikal:** {', '.join(categorical_cols) if categorical_cols else 'Tidak ada'}")

        # ========== Bagian Statistik Deskriptif ==========
        with st.expander("📊 Statistik Deskriptif Awal"):
            if numeric_cols:
                st.write(df[numeric_cols].describe())
            else:
                st.info("Tidak ada kolom numerik yang dapat dianalisis.")

    except Exception as e:
        st.error(f"Terjadi kesalahan saat membaca file: {e}")

else:
    st.info("Silakan unggah file Excel untuk memulai analisis.")
