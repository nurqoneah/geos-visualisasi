import streamlit as st
import pandas as pd
import plotly.express as px
import json

# Fungsi untuk memuat GeoJSON berdasarkan tingkat wilayah (kecamatan/kelurahan)
def load_geojson(geo_level):
    if geo_level == "Kelurahan":
        with open(".\\geos\\DESA\\Desa NOP Pekanbaru.geojson") as file_json:
            return json.load(file_json)
    elif geo_level == "Kecamatan":
        with open(".\\geos\\KECAMATAN\\kecamatan nop pekanbaru.geojson") as file_json:
            return json.load(file_json)

# Fungsi untuk memilih kolom
def select_column(label, df):
    return st.selectbox(f"Pilih kolom untuk {label}:", df.columns)

st.title("Visualisasi Geospatial: Kecamatan dan Kelurahan")

# Upload file
def render_map():
    uploaded_file = st.file_uploader("Unggah file CSV atau Excel", type=['csv', 'xlsx'])
    if uploaded_file:
        # Membaca file
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('csv') else pd.read_excel(uploaded_file)
        st.write("Data Preview:")
        st.dataframe(df)

        # Layout rapih menggunakan columns
        col1, col2 = st.columns(2)

        with col1:
            # Pilih tingkat wilayah (Kecamatan/Kelurahan)
            geo_level = st.selectbox("Pilih tingkat wilayah:", ["Kelurahan", "Kecamatan"])
            geojson_data = load_geojson(geo_level)

        with col2:
            # Pilih kolom untuk geolocation
            geo_column = select_column("kolom wilayah (kelurahan/kecamatan)", df)

        col1, col2 = st.columns(2)

        with col1:
            # Pilih kolom untuk nilai
            value_column = select_column("kolom nilai", df)

        with col2:
            # Tentukan tipe data (Numerik atau Kategori)
            value_type = st.selectbox("Tipe data nilai:", ["Numerik", "Kategori"])

        if value_type == 'Numerik':
        # Skema warna numerik
            color_option = st.radio("Pilih jenis skema warna:", ['Predefined', 'Custom'], horizontal=True)
            
            if color_option == 'Custom':
                st.write("Atur rentang warna:")
                ranges = []
                colors = []
                num_ranges = st.number_input("Jumlah rentang warna:", min_value=1, max_value=10, value=3, step=1)

                custom_colorscale = []
                st.write("Atur titik rentang dan warna:")
                for i in range(num_ranges):
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        point = st.number_input(f"Titik rentang {i+1} (0.0 - 1.0):", min_value=0.0, max_value=1.0, value=i/(num_ranges-1), key=f'point_{i}')
                    with col2:
                        color = st.color_picker(f"Pilih warna untuk rentang {point:.2f}:", '#008000' if i == 0 else '#FF0000', key=f'color_{i}')
                    custom_colorscale.append([point, color])

            else:
                predefined_color_scale = st.selectbox("Pilih skema warna:", ['Viridis', 'RdYlGn', 'Blues', 'Cividis', 'Inferno', 'Magma'])

            # Filter data untuk nilai numerik
            filtered_df = df
            filtered_df[value_column] = pd.to_numeric(filtered_df[value_column], errors='coerce')
            filtered_df = filtered_df.dropna(subset=[value_column])

        elif value_type == 'Kategori':
            # Kategori warna
            unique_categories = df[value_column].unique().tolist()
            color_map = {}
            st.write("Atur warna untuk setiap kategori:")
            for category in unique_categories:
                color = st.color_picker(f"Pilih warna untuk '{category}'", '#d73027')
                color_map[category] = color

            # Filter data
            filtered_df = df

        # Kolom tambahan untuk hover
        hover_columns = st.multiselect("Kolom tambahan untuk hover:", df.columns)
        hover_data = {col: True for col in hover_columns}

        # Visualisasi
        if value_type == 'Numerik':
            fig = px.choropleth_mapbox(
            filtered_df, 
            geojson=geojson_data, 
            locations=geo_column,  
            featureidkey=f"properties.DESA" if geo_level == 'Kelurahan' else f"properties.KECAMATAN",
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
                featureidkey=f"properties.DESA" if geo_level == 'Kelurahan' else f"properties.KECAMATAN",
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

        st.plotly_chart(fig)

