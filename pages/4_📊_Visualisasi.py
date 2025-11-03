import streamlit as st
import pandas as pd
import plotly.express as px

from utils.auth import is_logged_in

if not is_logged_in():
    st.warning("⚠️ Silakan login terlebih dahulu di halaman 🔐 Login.")
    st.stop()


# ================== PAGE CONFIG ==================
st.set_page_config(page_title="Visualisasi", page_icon="📊", layout="wide")
st.header("📊 Visualisasi")


# ================== DATA SOURCE (SESSION) ==================
df = st.session_state.get("uploaded_df", None)
if df is None:
    st.warning("⚠️ Belum ada data di memori. Silakan unggah file di halaman **📘 Data Excel** terlebih dulu.")
    st.stop()



# Pastikan kolom pertama adalah tanggal bila memungkinkan
date_col = df.columns[0]
if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
    try:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    except Exception:
        pass

numeric_cols = df.select_dtypes(include="number").columns.tolist()
if not numeric_cols:
    st.error("Tidak ada kolom numerik untuk divisualisasikan.")
    st.stop()

# ================== FILTER PANEL ==================
with st.expander("⚙️ Filter", expanded=True):
    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        target_y = st.selectbox("Kolom Y (utama)", numeric_cols, index=0)
    with c2:
        scatter_x = st.selectbox("Kolom X (untuk Scatter)", numeric_cols, index=1)
    with c3:
        mult_cols = st.multiselect("Kolom numerik (untuk Pie & Multi-series Bar)", numeric_cols)

    if pd.api.types.is_datetime64_any_dtype(df[date_col]):
        r1, r2 = st.columns(2)
        with r1:
            start_date = st.date_input("Tanggal mulai", pd.to_datetime(df[date_col].min()))
        with r2:
            end_date = st.date_input("Tanggal akhir", pd.to_datetime(df[date_col].max()))
        mask = (df[date_col] >= pd.to_datetime(start_date)) & (df[date_col] <= pd.to_datetime(end_date))
        fdf = df.loc[mask].copy()
    else:
        st.info(f"Kolom pertama (**{date_col}**) bukan tanggal. Filter tanggal dinonaktifkan.")
        fdf = df.copy()

st.divider()
st.subheader("📌 Score Cards")

# ambil kolom numerik utama
num_cols = fdf.select_dtypes(include="number").columns.tolist()

if not num_cols:
    st.info("Tidak ada kolom numerik untuk menampilkan score card.")
else:
    # ambil kolom utama (Y) untuk contoh
    main_col = target_y 

    total_rows = len(fdf)
    avg_val = fdf[main_col].mean()
    max_val = fdf[main_col].max()
    min_val = fdf[main_col].min()

    # hitung delta 7 hari terakhir (jika ada kolom tanggal)
    delta_text = None
    if pd.api.types.is_datetime64_any_dtype(fdf[date_col]):
        last_week = fdf[fdf[date_col] >= (fdf[date_col].max() - pd.Timedelta(days=7))]
        prev_week = fdf[(fdf[date_col] < (fdf[date_col].max() - pd.Timedelta(days=7))) &
                        (fdf[date_col] >= (fdf[date_col].max() - pd.Timedelta(days=14)))]
        if not last_week.empty and not prev_week.empty:
            delta_val = last_week[main_col].mean() - prev_week[main_col].mean()
            delta_text = f"{delta_val:.2f}"

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📦 Jumlah Baris", f"{total_rows:,}")
    c2.metric(f"📊 Rata-rata ({main_col})", f"{avg_val:,.2f}", delta=delta_text)
    c3.metric(f"⬆️ Maks ({main_col})", f"{max_val:,.2f}")
    c4.metric(f"⬇️ Min ({main_col})", f"{min_val:,.2f}")

# ================== HELPERS ==================
def monthly_agg(dataframe, y_cols):
    out = dataframe.copy()
    if pd.api.types.is_datetime64_any_dtype(out[date_col]):
        out["__month__"] = out[date_col].dt.to_period("M").dt.to_timestamp()
        return out.groupby("__month__", as_index=False)[y_cols].sum().sort_values("__month__")
    # fallback tanpa tanggal
    out["__row__"] = range(len(out))
    return out

# ================== ROW 1: LINE & BAR ==================
st.divider()


col_left, col_right = st.columns(2, gap="small")

with st.expander("📈 Line Chart (Multi-series)", expanded=False):
    if len(mult_cols) == 0:
        st.warning("Pilih ≥1 kolom di **Kolom numerik (untuk Pie & Multi-series Bar)** agar multi-series tampil.")
    else:
        # batasi terlalu banyak seri agar tetap terbaca
        cols_for_line = mult_cols
        line_df = fdf[[date_col] + cols_for_line].dropna().sort_values(by=date_col)
        fig_multi = px.line(
            line_df,
            x=date_col,
            y=cols_for_line,         # wide-form: otomatis bikin beberapa trace
            markers=False,
            template="plotly_dark",
            title="Tren Waktu (Multi-series)"
        )
        # fig_multi.update_layout(
        #     xaxis_title="Tanggal",
        #     yaxis_title="Nilai",
        #     legend_title="Seri",
        #     hovermode="x unified",
        #     xaxis=dict(tickformat="%d/%m/%Y", tickangle=-45)
        # )
        st.plotly_chart(fig_multi, use_container_width=True)

with col_left:
    with st.expander("📈 Line Chart", expanded=True):
        if pd.api.types.is_datetime64_any_dtype(fdf[date_col]):
            chart_df = fdf[[date_col, target_y]].sort_values(by=date_col)
            fig = px.line(chart_df, x=date_col, y=target_y, markers=True, template="plotly_dark",
                          title="Tren Waktu")
            # fig.update_layout(hovermode="x unified", height=420, margin=dict(l=10, r=10, t=60, b=10),
            #                   xaxis_title="Tanggal", yaxis_title=target_y)

            fig.update_layout(
                xaxis_title="Tanggal",
                yaxis_title="Nilai",
                legend_title="Kolom",
                hovermode="x unified",
                xaxis=dict(tickformat="%d/%m/%Y", tickangle=-45)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Line chart memerlukan kolom tanggal yang valid di kolom pertama.")

# with col_right:
#     with st.expander("📊 Bar Chart (Agregasi Bulanan)", expanded=True):
#         cols_for_bar = mult_cols if len(mult_cols) > 0 else [target_y]
#         agg_df = monthly_agg(fdf, cols_for_bar)
#         y_arg = cols_for_bar if len(cols_for_bar) > 1 else cols_for_bar[0]
#         x_arg = "__month__" if "__month__" in agg_df.columns else agg_df.columns[0]
#         fig = px.bar(agg_df, x=x_arg, y=y_arg, barmode="group", template="plotly_dark",
#                      title="Agregasi Bulanan")
#         # fig.update_layout(height=420, margin=dict(l=10, r=10, t=60, b=10),
#         #                   xaxis_title="Periode", yaxis_title="Nilai", legend_title="Kolom")
#         st.plotly_chart(fig, use_container_width=True)

with col_right:
    with st.expander("📊 Bar Chart", expanded=True):
        cols_for_bar = mult_cols if len(mult_cols) > 0 else [target_y]
        y_arg = cols_for_bar if len(cols_for_bar) > 1 else cols_for_bar[0]

        # gran = st.radio(
        #     "Granularitas",
        #     ["Harian", "Mingguan", "Bulanan"],
        #     horizontal=True,
        #     index=0
        # )

        tmp = fdf[[date_col] + cols_for_bar].dropna().copy()

        # if gran == "Mingguan":
        #     tmp = tmp.set_index(date_col).resample("W")[cols_for_bar].sum().reset_index()
        # elif gran == "Bulanan":
        #     tmp = tmp.set_index(date_col).resample("M")[cols_for_bar].sum().reset_index()
        # else:
        #     tmp = tmp.sort_values(by=date_col)

        fig = px.bar(
            tmp.sort_values(by=date_col),
            x=date_col,
            y=y_arg,
            barmode="group",
            template="plotly_dark",
            title="Bar Chart"
        )

        # Kunci agar “column” tidak tampak area
        one_day_ms = 24*60*60*1000
        fig.update_traces(width=one_day_ms*0.80)      # lebar batang (jalan juga untuk weekly)
        fig.update_layout(
            bargap=0.30,                              # jarak antar tanggal
            bargroupgap=0.10,                         # jarak antar seri pada tanggal yg sama
            xaxis_title="Tanggal",
            yaxis_title="Nilai",
            legend_title="Kolom",
            hovermode="x unified",
            xaxis=dict(tickformat="%d/%m/%Y", tickangle=-45)
        )

        # Kalau tetap terlalu rapat (dataset super padat), pakai kategori string:
        # tmp["__tgl__"] = tmp[date_col].dt.strftime("%Y-%m-%d")
        # fig = px.bar(tmp, x="__tgl__", y=y_arg, barmode="group", template="plotly_dark")

        st.plotly_chart(fig, use_container_width=True)



# ================== ROW 2: PIE & SCATTER ==================
col_left2, col_right2 = st.columns(2, gap="small")

with col_left2:
    with st.expander("🥧 Pie Chart", expanded=True):
        cols_for_pie = mult_cols 
        # Sum total periode terpilih untuk tiap kolom → komposisi
        totals = fdf[cols_for_pie].sum(numeric_only=True)
        pie_df = pd.DataFrame({"Variabel": totals.index, "Total": totals.values})
        fig = px.pie(pie_df, names="Variabel", values="Total", hole=0.4, template="plotly_dark",
                     title="Komposisi (Total pada Rentang Terpilih)")
        # fig.update_layout(height=420, margin=dict(l=10, r=10, t=60, b=10))
        st.plotly_chart(fig, use_container_width=True)

with col_right2:
    with st.expander("🟣 Scatter Plot", expanded=True):
        sc_df = fdf[[scatter_x, target_y]].dropna()
        fig = px.scatter(sc_df, x=scatter_x, y=target_y, trendline="ols", template="plotly_dark",
                         title="Korelasi")
        # fig.update_layout(height=420, margin=dict(l=10, r=10, t=60, b=10),
        #                   xaxis_title=scatter_x, yaxis_title=target_y)
        st.plotly_chart(fig, use_container_width=True)

# ================== FOOTER ==================
