import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import json
import matplotlib.colors as mcolors
import matplotlib.cm as cm


# Fungsi untuk memuat GeoJSON berdasarkan tingkat wilayah (kecamatan/kelurahan)
def load_geojson(geo_level):
    if geo_level == "Kelurahan":
        with open("geos/DESA/Desa NOP Pekanbaru.geojson") as file_json:
            return json.load(file_json)
    elif geo_level == "Kecamatan":
        with open("geos/KECAMATAN/kecamatan nop pekanbaru.geojson") as file_json:
<<<<<<< HEAD
            return json.load(file_json)
    elif geo_level == "Kota":
        with open("geos/KOTA/Indonesia_cities.geojson") as file_json:
=======
>>>>>>> ec8ce1395cb18ac9ba7443ddc5de04fe244bd687
            return json.load(file_json)
        
def map_numeric_to_color(value, vmin, vmax, cmap_name="viridis"):
    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)  # Normalisasi nilai
    cmap = cm.get_cmap(cmap_name)  # Pilih skema warna
    return mcolors.to_hex(cmap(norm(value)))  # Konversi ke HEX

# Fungsi untuk memilih kolom
def select_column(label, df):
    return st.selectbox(f"Pilih kolom untuk {label}:", df.columns)

# Fungsi render untuk peta (Map)
def render_map():
    uploaded_file = st.file_uploader("Unggah file CSV atau Excel", type=['csv', 'xlsx'])
    if uploaded_file:
        # Membaca file
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('csv') else pd.read_excel(uploaded_file)
        st.write("Data Preview:")
        st.dataframe(df)

        # Konfigurasi melalui Sidebar
        with st.sidebar:
            st.header("Konfigurasi Peta")

            # Pilih tingkat wilayah (Kecamatan/Kelurahan)
            geo_level = st.selectbox("Pilih tingkat wilayah:", ["Kelurahan", "Kecamatan", "Kota"])
            geojson_data = load_geojson(geo_level)

            # Pilih kolom untuk geolocation
            geo_column = select_column("Kolom wilayah (kelurahan/kecamatan/kota):", df)
            if geo_level=="Kota":
                mapping = {
                    'KOTA PEKANBARU': 'Pekanbaru',
                    'BENGKALIS': 'Bengkalis',
                    'KOTA DUMAI': 'Dumai',
                    'INDRAGIRI HULU': 'Indragiri Hulu',
                    'KAMPAR': 'Kampar',
                    'KEPULAUAN MERANTI': 'Kepulauan Meranti',
                    'KUANTAN SINGINGI': 'Kuantan Singingi',
                    'ROKAN HILIR': 'Rokan Hilir',
                    'ROKAN HULU': 'Rokan Hulu',
                    'S I A K': 'Siak',
                    'INDRAGIRI HILIR': 'Indragiri Hilir',
                    'PELALAWAN': 'Pelalawan'
                }

                # Menerapkan pemetaan ke kolom geo_column
                df[geo_column] = df[geo_column].map(mapping)



            # Pilih kolom untuk nilai
            value_column = select_column("Kolom nilai:", df)

            # Tentukan tipe data (Numerik atau Kategori)
            value_type = st.selectbox("Tipe data nilai:", ["Numerik", "Kategori"])

            if value_type == 'Numerik':
                # Skema warna numerik
                color_option = st.radio("Pilih jenis skema warna:", ['Predefined', 'Custom'], horizontal=True)
                
                if color_option == 'Custom':
                    st.write("Atur rentang warna:")
                    custom_colorscale = []
                    num_ranges = st.number_input("Jumlah rentang warna:", min_value=1, max_value=10, value=3, step=1)

                    for i in range(num_ranges):
                        col1, col2 = st.columns([1, 2])
                        with col1:
                            point = st.number_input(f"Titik rentang {i+1} (0.0 - 1.0):", min_value=0.0, max_value=1.0, value=i/(num_ranges-1), key=f'point_{i}')
                        with col2:
                            color = st.color_picker(f"Pilih warna untuk rentang {point:.2f}:", '#008000' if i == 0 else '#FF0000', key=f'color_{i}')
                        custom_colorscale.append([point, color])
                else:
                    predefined_color_scale = st.selectbox("Pilih skema warna:", ['Viridis', 'RdYlGn', 'Blues', 'Cividis', 'Inferno', 'Magma'])

            elif value_type == 'Kategori':
                # Kategori warna
                unique_categories = df[value_column].unique().tolist()
                color_map = {}
                st.write("Atur warna untuk setiap kategori:")
                for category in unique_categories:
                    color = st.color_picker(f"Pilih warna untuk '{category}'", '#d73027')
                    color_map[category] = color

            # Kolom tambahan untuk hover
            hover_columns = st.multiselect("Kolom tambahan untuk hover:", df.columns)
            hover_data = {col: True for col in hover_columns}

        # Filter data untuk nilai numerik
        if value_type == 'Numerik':
            filtered_df = df
            filtered_df[value_column] = pd.to_numeric(filtered_df[value_column], errors='coerce')
            filtered_df = filtered_df.dropna(subset=[value_column])

        elif value_type == 'Kategori':
            filtered_df = df

        # Visualisasi
        st.subheader("Visualisasi Peta")
        if value_type == 'Numerik':
            fig = px.choropleth_mapbox(
                filtered_df, 
                geojson=geojson_data, 
                locations=geo_column,  
                featureidkey = f"properties.DESA" if geo_level == 'Kelurahan' else f"properties.KECAMATAN" if geo_level == 'Kecamatan' else "properties.NAME_2",
                color=value_column, 
                color_continuous_scale=custom_colorscale if color_option == 'Custom' else predefined_color_scale,
                range_color=(filtered_df[value_column].min(), filtered_df[value_column].max()),
                hover_data=hover_data,
                labels={value_column: value_column},
            )
        else:
            fig = px.choropleth_mapbox(
                filtered_df, 
                geojson=geojson_data, 
                locations=geo_column,  
                featureidkey = f"properties.DESA" if geo_level == 'Kelurahan' else f"properties.KECAMATAN" if geo_level == 'Kecamatan' else "properties.NAME_2",
                color=value_column, 
                color_discrete_map=color_map,  # Warna kategori
                hover_data=hover_data,
                labels={value_column: value_column},
            )

        # Layout peta
        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(
            mapbox_style="carto-positron",  
            mapbox_zoom=6.5,  
            mapbox_center={"lat": 0.091, "lon": 102.349}, 
            margin={"r": 0, "t": 0, "l": 0, "b": 0}
        )

        return st.plotly_chart(fig)

# Fungsi render untuk Scatter Plot
def render_scatter():
    # Upload file
    uploaded_file = st.file_uploader("Upload file Excel Anda", type=["xlsx", "xls"])
    if uploaded_file:
        # Load data
        df = pd.read_excel(uploaded_file)
        st.write("Data yang diunggah:")
        st.write(df.head())

        # Konfigurasi Scatter Plot di Sidebar
        st.sidebar.header("Konfigurasi Scatter Plot")
        long_column = st.sidebar.selectbox("Pilih kolom Longitude:", df.columns)
        lat_column = st.sidebar.selectbox("Pilih kolom Latitude:", df.columns)
        color_column = st.sidebar.selectbox("Pilih kolom untuk Color:", df.columns)
        size_column = st.sidebar.selectbox("Pilih kolom untuk Size (Opsional):", ['None'] + list(df.columns))
        hover_columns = st.sidebar.multiselect("Pilih kolom tambahan untuk Hover:", df.columns)

        value_type = st.sidebar.radio("Tipe kolom Color:", ['Numerik', 'Kategori'], horizontal=True)

        # Konfigurasi untuk Numerik
        if value_type == 'Numerik':
            color_option = st.sidebar.radio("Pilih jenis skema warna:", ['Predefined', 'Custom'], horizontal=True)
            if color_option == 'Custom':
                st.write("Atur rentang warna:")
                custom_colorscale = []
                num_ranges = st.number_input("Jumlah rentang warna:", min_value=1, max_value=10, value=3, step=1)

                for i in range(num_ranges):
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        point = st.number_input(f"Titik rentang {i+1} (0.0 - 1.0):", min_value=0.0, max_value=1.0, value=i/(num_ranges-1), key=f'point_{i}')
                    with col2:
                        color = st.color_picker(f"Pilih warna untuk rentang {point:.2f}:", '#008000' if i == 0 else '#FF0000', key=f'color_{i}')
                    custom_colorscale.append([point, color])
            else:
                predefined_color_scale = st.selectbox("Pilih skema warna:", ['Viridis', 'RdYlGn', 'Blues', 'Cividis', 'Inferno', 'Magma'])

        # Konfigurasi untuk Kategori
        elif value_type == 'Kategori':
            unique_categories = df[color_column].unique().tolist()
            color_map = {}
            st.sidebar.write("Atur warna untuk setiap kategori:")
            for category in unique_categories:
                color_map[category] = st.sidebar.color_picker(f"Warna untuk '{category}'", '#d73027')

        # Filter data
        filtered_df = df.copy()
        if value_type == 'Numerik':
            filtered_df[color_column] = pd.to_numeric(filtered_df[color_column], errors='coerce')
            filtered_df = filtered_df.dropna(subset=[color_column])

        size_arg = None if size_column == 'None' else size_column

        # Visualisasi Scatter Plot
        st.subheader("Hasil Visualisasi Scatter Plot")
        if value_type == 'Numerik':
            fig = px.scatter_mapbox(
                filtered_df,
                lat=lat_column,
                lon=long_column,
                color=color_column,
                size=size_arg,
                color_continuous_scale=custom_colorscale if color_option == 'Custom' else predefined_color_scale,
                hover_data=hover_columns,
                size_max=15,
                zoom=5,
            )
        elif value_type == 'Kategori':
            fig = px.scatter_mapbox(
                filtered_df,
                lat=lat_column,
                lon=long_column,
                color=color_column,
                size=size_arg,
                hover_data=hover_columns,
                color_discrete_map=color_map,
                size_max=15,
                zoom=5,
            )

        fig.update_layout(
            mapbox_style="carto-positron",  
            mapbox_zoom=6.5,  
            mapbox_center={"lat": 0.091, "lon": 102.349}, 
            margin={"r": 0, "t": 0, "l": 0, "b": 0}
        )
        return st.plotly_chart(fig)
        
def render_line():
    uploaded_file = st.file_uploader("Unggah file Excel", type=["xlsx", "xls"])

    if uploaded_file:
        # Load data
        df = pd.read_excel(uploaded_file)

        # Menampilkan preview data di layar utama
        st.write("Preview Data:")
        st.dataframe(df)

        # Konfigurasi di sidebar
        st.sidebar.header("Konfigurasi Visualisasi Garis")

        # Kolom untuk Latitude dan Longitude Asal & Tujuan
        col_lat_asal = st.sidebar.selectbox("Kolom Latitude Asal", df.columns)
        col_lon_asal = st.sidebar.selectbox("Kolom Longitude Asal", df.columns)
        col_lat_tujuan = st.sidebar.selectbox("Kolom Latitude Tujuan", df.columns)
        col_lon_tujuan = st.sidebar.selectbox("Kolom Longitude Tujuan", df.columns)

        # Pengaturan warna
        st.sidebar.subheader("Pengaturan Warna:")
        color_column = st.sidebar.selectbox("Kolom untuk Warna", df.columns)
        color_type = st.sidebar.radio("Tipe Data untuk Warna:", ["Numerik", "Kategori"], horizontal=True)

        # Pengaturan ukuran garis
        st.sidebar.subheader("Pengaturan Ukuran Garis:")
        size_column = st.sidebar.selectbox("Kolom untuk Ukuran Garis (Opsional)", ["None"] + list(df.columns))
        default_size = st.sidebar.slider("Ukuran Garis Default", min_value=1, max_value=10, value=2)

        # Hover tambahan
        hover_columns = st.sidebar.multiselect("Kolom Tambahan untuk Hover:", df.columns)

        # Logika warna untuk numerik
        if color_type == "Numerik":
            color_option = st.sidebar.radio("Pilih jenis skema warna:", ['Predefined', 'Custom'], horizontal=True)
            if color_option == 'Custom':
                st.write("Atur rentang warna:")
                custom_colorscale = []
                num_ranges = st.number_input("Jumlah rentang warna:", min_value=1, max_value=10, value=3, step=1)

                for i in range(num_ranges):
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        point = st.number_input(f"Titik rentang {i+1} (0.0 - 1.0):", min_value=0.0, max_value=1.0, value=i/(num_ranges-1), key=f'point_{i}')
                    with col2:
                        color = st.color_picker(f"Pilih warna untuk rentang {point:.2f}:", '#008000' if i == 0 else '#FF0000', key=f'color_{i}')
                    custom_colorscale.append([point, color])

                # Urutkan custom_colorscale berdasarkan titik rentang
                custom_colorscale = sorted(custom_colorscale, key=lambda x: x[0])

                # Terapkan skala warna kustom
                min_val = df[color_column].min()
                max_val = df[color_column].max()

                # Normalisasi nilai numerik berdasarkan rentang yang diatur pengguna
                df["color"] = df[color_column].apply(
                    lambda x: next((color for point, color in custom_colorscale if x <= (min_val + (max_val - min_val) * point)), custom_colorscale[-1][1])
                )

            else:
                predefined_color_scale = st.selectbox("Pilih skema warna:", ['Viridis', 'RdYlGn', 'Blues', 'Cividis', 'Inferno', 'Magma'])
                # Buat skala warna untuk numerik berdasarkan pilihan predefined
                color_scale = px.colors.sequential.__dict__.get(predefined_color_scale)
                df["color"] = df[color_column].apply(
                    lambda x: color_scale[int(((x - df[color_column].min()) / (df[color_column].max() - df[color_column].min())) * (len(color_scale) - 1))]
                )
        elif color_type == "Kategori":
            # Pengguna dapat menentukan warna untuk setiap kategori
            unique_categories = df[color_column].unique()
            color_map = {}
            for category in unique_categories:
                color_map[category] = st.sidebar.color_picker(f"Warna untuk {category}", "#000000")  # Pilih warna untuk tiap kategori
            df["color"] = df[color_column].map(color_map)

        # Pastikan 'size' kolom ditambahkan dengan benar
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

        # Atur tata letak peta
        fig.update_layout(
            mapbox_style="carto-positron",  
            mapbox_zoom=6.5,  
            mapbox_center={"lat": 0.091, "lon": 102.349}, 
            margin={"r": 0, "t": 0, "l": 0, "b": 0}
        )

        return st.plotly_chart(fig)

# Custom color assignment function

# Fungsi utama
def main():
    st.title("Visualisasi Data Geospasial dan Statistik")

    # Sidebar untuk memilih jenis visualisasi
    visualisasi = st.sidebar.selectbox(
        "Pilih jenis visualisasi:",
        ["Peta Choropleth", "Scatter Plot", "Line Chart"]
    )

    if visualisasi == "Peta Choropleth":
        fig = render_map()

    elif visualisasi == "Scatter Plot":
        fig = render_scatter()
        

    elif visualisasi == "Line Chart":
        fig = render_line()
        
   

# Menjalankan aplikasi
if __name__ == "__main__":
    main()

