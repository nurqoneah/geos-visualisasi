import pandas as pd
import streamlit as st
import plotly.graph_objs as go
import matplotlib.colors as mcolors
import matplotlib.cm as cm

# Fungsi untuk memetakan nilai numerik ke skala warna
def map_numeric_to_color(value, vmin, vmax, cmap_name="viridis"):
    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)  # Normalisasi nilai
    cmap = cm.get_cmap(cmap_name)  # Pilih skema warna
    return mcolors.to_hex(cmap(norm(value)))  # Konversi ke HEX

# Fungsi utama
def main():
    st.title("Visualisasi Garis Line pada Scattermapbox")
    st.write("Unggah file Excel yang berisi data asal dan tujuan (long, lat), warna, dan ukuran garis.")

    # Input file dari pengguna
    uploaded_file = st.file_uploader("Unggah file Excel", type=["xlsx", "xls"])

    if uploaded_file:
        # Load data
        df = pd.read_excel(uploaded_file)

        # Menampilkan preview data
        st.write("Preview Data:")
        st.dataframe(df)

        # Kolom yang diperlukan
        st.subheader("Pilih Kolom Input:")
        col_lat_asal = st.selectbox("Kolom Latitude Asal", df.columns)
        col_lon_asal = st.selectbox("Kolom Longitude Asal", df.columns)
        col_lat_tujuan = st.selectbox("Kolom Latitude Tujuan", df.columns)
        col_lon_tujuan = st.selectbox("Kolom Longitude Tujuan", df.columns)

        # Opsi warna
        st.subheader("Pengaturan Warna:")
        color_column = st.selectbox("Pilih Kolom Warna", df.columns)
        color_type = st.radio("Tipe Warna", ["Numerik", "Kategori"])

        # Opsi ukuran garis
        st.subheader("Pengaturan Ukuran Garis:")
        size_column = st.selectbox("Pilih Kolom Ukuran Garis (Opsional)", ["None"] + list(df.columns))
        default_size = st.slider("Ukuran Garis Default", min_value=1, max_value=10, value=2)

        # Hover tambahan
        st.subheader("Informasi Tambahan untuk Hover:")
        hover_columns = st.multiselect("Pilih Kolom untuk Hover", df.columns)

        # Normalisasi warna jika numerik
        if color_type == "Numerik":
            vmin = df[color_column].min()
            vmax = df[color_column].max()
            df["color"] = df[color_column].apply(lambda x: map_numeric_to_color(x, vmin, vmax))
        else:
            unique_categories = df[color_column].unique()
            category_colors = {cat: f"rgba({i*50%256},{(i*100)%256},{(i*150)%256},0.8)" for i, cat in enumerate(unique_categories)}
            df["color"] = df[color_column].map(category_colors)

        # Ukuran garis
        if size_column != "None":
            vmin_size = df[size_column].min()
            vmax_size = df[size_column].max()
            df["size"] = df[size_column].apply(lambda x: ((x - vmin_size) / (vmax_size - vmin_size) * 8) + 2)
        else:
            df["size"] = default_size

        # Plotly Scattermapbox
        st.subheader("Visualisasi Peta:")
        fig = go.Figure()

        for i, row in df.iterrows():
            # Tambahkan garis dari titik asal ke tujuan
            fig.add_trace(
                go.Scattermapbox(
                    mode="lines",
                    lon=[row[col_lon_asal], row[col_lon_tujuan]],
                    lat=[row[col_lat_asal], row[col_lat_tujuan]],
                    line=dict(width=row["size"], color=row["color"]),
                    hoverinfo="text",
                    text=f"<b>Warna:</b> {row[color_column]}<br>" + 
                         "<br>".join([f"{col}: {row[col]}" for col in hover_columns])
                )
            )

        # Layout peta
        fig.update_layout(
            mapbox=dict(
                style="open-street-map",  # Gunakan OpenStreetMap
                zoom=5,
                center=dict(lat=df[col_lat_asal].mean(), lon=df[col_lon_asal].mean()),
            ),
            margin=dict(l=0, r=0, t=0, b=0)
        )

        # Tampilkan peta
        st.plotly_chart(fig)

if __name__ == "__main__":
    main()
