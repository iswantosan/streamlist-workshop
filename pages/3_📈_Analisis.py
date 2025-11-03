import streamlit as st
import pandas as pd
import plotly.express as px

from utils.auth import is_logged_in

if not is_logged_in():
    st.warning("⚠️ Silakan login terlebih dahulu di halaman 🔐 Login.")
    st.stop()


st.header("📈 Analisis Deskriptif")

# --- Ambil DataFrame dari session_state ---
df = st.session_state.get("uploaded_df", None)
if df is None:
    st.warning("⚠️ Belum ada data di memori. Silakan unggah file di halaman **📘 Data Excel** terlebih dulu.")
    st.stop()

# --- Pastikan kolom 1 sebagai tanggal (jika memungkinkan) ---
date_col = df.columns[0]
# if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
#     with st.expander("🛠️ Konversi Tanggal (opsional)", expanded=False):
#         st.caption(f"Kolom pertama: **{date_col}** belum bertipe tanggal. Mencoba konversi otomatis…")
#     try:
#         df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
#     except Exception:
#         pass

numeric_cols = df.select_dtypes(include="number").columns.tolist()
if not numeric_cols:
    st.error("Tidak ditemukan kolom numerik untuk dianalisis.")
    st.stop()

# =================== FILTER (Accordion) ===================
with st.expander("⚙️ Filter Analisis", expanded=True):
    target_col = st.selectbox("Pilih kolom numerik", numeric_cols, index=0)

    if pd.api.types.is_datetime64_any_dtype(df[date_col]):
        c1, c2 = st.columns(2)
        with c1:
            start_date = st.date_input("Tanggal mulai", pd.to_datetime(df[date_col].min()))
        with c2:
            end_date = st.date_input("Tanggal akhir", pd.to_datetime(df[date_col].max()))
        mask = (df[date_col] >= pd.to_datetime(start_date)) & (df[date_col] <= pd.to_datetime(end_date))
        fdf = df.loc[mask].copy()
        st.caption(f"Baris terpilih: **{len(fdf):,}**")
    else:
        st.info(f"Kolom pertama (**{date_col}**) bukan tanggal, filter tanggal dinonaktifkan.")
        fdf = df.copy()

# =================== DATA TERFILTER (Accordion) ===================
with st.expander("📊 Data Terfilter", expanded=False):
    st.dataframe(fdf, use_container_width=True)

# =================== METRIK RINGKAS (Accordion) ===================
with st.expander("📋 Indikator", expanded=True):
    mean_val  = fdf[target_col].mean()
    sum_val   = fdf[target_col].sum()
    min_val   = fdf[target_col].min()
    max_val   = fdf[target_col].max()
    count_val = fdf[target_col].count()

    c1, c2, c3, c4, c5 = st.columns(5)
    #c1.metric("Rata-rata (mean)", f"{mean_val:,.4f}")
    c1.metric("Rata-rata (mean)", round(mean_val, 4))
    c2.metric("Total (sum)",      f"{sum_val:,.2f}")
    c3.metric("Minimum",          f"{min_val:,.4f}")
    c4.metric("Maksimum",         f"{max_val:,.4f}")
    c5.metric("Jumlah data",      f"{count_val:,}")

# =================== STATISTIK DESKRIPTIF (Accordion) ===================
with st.expander(f"🧮 Statistik Deskriptif: {target_col}", expanded=False):
    st.write(fdf[target_col].describe())