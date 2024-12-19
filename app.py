import streamlit as st
import pandas as pd
import plotly.express as px
import json

# Fungsi untuk memuat GeoJSON berdasarkan tingkat wilayah (kecamatan/kelurahan)
def load_geojson(geo_level):
    if geo_level == "Kelurahan":
        with open("geos/DESA/Desa NOP Pekanbaru.geojson") as file_json:
            return json.load(file_json)
    elif geo_level == "Kecamatan":
        with open("geos/KECAMATAN/kecamatan nop pekanbaru.geojson") as file_json:
            return json.load(file_json)

# Fungsi untuk memilih kolom
def select_column(label, df):
    return st.selectbox(f"Pilih kolom untuk {label}:", df.columns)

# Fungsi untuk mengurutkan kategori secara drag and drop
def sort_categories(column, df):
    unique_values = sorted(df[column].unique().tolist())
    return st.multiselect(f"Urutkan kategori {column}:", unique_values, default=unique_values)


st.title("Visualisasi Geospatial: Kecamatan dan Kelurahan")

# Memuat file CSV atau Excel
uploaded_file = st.file_uploader("Unggah file CSV atau Excel", type=['csv', 'xlsx'])
if uploaded_file:
    if uploaded_file.name.endswith('csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.write("Data Preview:")
    st.dataframe(df)

    # Pilih geo-level antara Kecamatan dan Kelurahan
    geo_level = st.selectbox("Pilih tingkat wilayah untuk visualisasi:", ["Kelurahan", "Kecamatan"])
    
    # Memuat GeoJSON sesuai dengan pilihan user
    geojson_data = load_geojson(geo_level)

    # Pilih kolom untuk geolocation (kelurahan/kecamatan)
    geo_column = select_column("kolom wilayah (kelurahan/kecamatan)", df)

    # Pilih kolom untuk value (numerik/kategori)
    value_column = select_column("kolom nilai", df)

    # Tentukan tipe data (Numerik atau Kategori)
    value_type = st.selectbox("Tipe data nilai:", ["Numerik", "Kategori"])

    # Input zoom map dan posisi peta
    # map_zoom = st.slider("Pilih level zoom peta:", 5, 12, 6)
    # map_center_lat = st.number_input("Latitude untuk pusat peta:", value=0.091)
    # map_center_lon = st.number_input("Longitude untuk pusat peta:", value=102.349)

    # Pengaturan warna untuk numerik
    if value_type == 'Numerik':
        color_option = st.radio("Pilih jenis skema warna:", ('Skema warna kustom', 'Skema warna pre-defined'))
        
        if color_option == 'Skema warna kustom':
            st.write("Pilih warna untuk tiap rentang nilai (skala 0-1):")
            
            ranges = [
                (0.0, 0.1, '#004000'),  # Hijau gelap (0.0 - 0.1)
                (0.1, 0.2, '#006400'),  # Hijau tua (0.1 - 0.2)
                (0.2, 0.3, '#008000'),  # Hijau (0.2 - 0.3)
                (0.3, 0.4, '#32CD32'),  # Hijau terang (0.3 - 0.4)
                (0.4, 0.5, '#ADFF2F'),  # Hijau kekuningan (0.4 - 0.5)
                (0.5, 0.6, '#FFFF00'),  # Kuning (0.5 - 0.6)
                (0.6, 0.7, '#FFD700'),  # Kuning emas (0.6 - 0.7)
                (0.7, 0.8, '#FFA500'),  # Oranye (0.7 - 0.8)
                (0.8, 0.9, '#FF4500'),  # Oranye kemerahan (0.8 - 0.9)
                (0.9, 1.0, '#FF0000'),  # Merah (0.9 - 1.0)
            ]

            # ranges = [
            #     (0.0, 0.1, '#004000'),  # Hijau terang (0.0 - 0.1)
            #     (0.1, 0.2, '#7CFC00'),  # Hijau kekuningan terang (0.1 - 0.2)
            #     (0.2, 0.3, '#ADFF2F'),  # Hijau kekuningan (0.2 - 0.3)
            #     (0.3, 0.4, '#FFFF00'),  # Kuning (0.3 - 0.4)
            #     (0.4, 0.6, '#FFD700'),  # Kuning emas (0.4 - 0.6)
            #     (0.6, 0.8, '#FFA500'),  # Oranye (0.6 - 0.8)
            #     (0.8, 1.0, '#FF0000'),  # Merah (0.8 - 1.0)
            # ]

            custom_colorscale = [
                [0.0, '#004000'],  
                [0.2, '#FFFF00'],   # Warna sedang
                [0.4, '#FFD700'],   # Warna sedang # Warna rendah
                [0.6, '#FF4500'],   # Warna sedang
                [1.0, '#860000']   # Warna tinggi
            ]
        else:
            # Pilih dari skema warna pre-defined Plotly
            predefined_color_scale = st.selectbox("Pilih skema warna pre-defined:",
                                              ['Viridis', 'RdYlGn', 'Blues', 'Cividis', 'Inferno', 'Magma'])
        
        filtered_df = df  
        filtered_df[value_column] = pd.to_numeric(filtered_df[value_column], errors='coerce')
        filtered_df = filtered_df.dropna(subset=[value_column])

    # Pengaturan kategori dengan drag and drop
    elif value_type == 'Kategori':
        sorted_categories = sort_categories(value_column, df)
        filtered_df = df[df[value_column].isin(sorted_categories)]

        # Mapping warna untuk kategori
        color_map = {}
        
        # Membuat color picker untuk setiap kategori yang dipilih
        for category in sorted_categories:
            color = st.color_picker(f"Pilih warna untuk kategori '{category}'", '#d73027')  # Default color
            color_map[category] = color

    # Visualisasi
    # Pilih kolom tambahan untuk hover label
    hover_columns = st.multiselect("Pilih kolom untuk ditampilkan di hover label:", df.columns)

    # Pastikan data dalam kolom hover bisa digunakan (misalnya, konversi ke string jika diperlukan)
    hover_data = {col: True for col in hover_columns}

    # Visualisasi
    # Visualisasi
    if value_type == 'Numerik':
        fig = px.choropleth_mapbox(
            filtered_df, 
            geojson=geojson_data, 
            locations=geo_column,  
            featureidkey=f"properties.DESA" if geo_level == 'Kelurahan' else f"properties.KECAMATAN",  # Sesuaikan dengan key GeoJSON
            color=value_column, 
            color_continuous_scale=custom_colorscale if color_option == 'Skema warna kustom' else predefined_color_scale, 
            range_color=(filtered_df[value_column].min(), filtered_df[value_column].max()),
            labels={value_column: value_column},
            # text=value_column
        )
    else:
        fig = px.choropleth_mapbox(
            filtered_df, 
            geojson=geojson_data, 
            locations=geo_column,  
            featureidkey=f"properties.DESA" if geo_level == 'Kelurahan' else f"properties.KECAMATAN",  # Sesuaikan dengan key GeoJSON
            color=value_column, 
            color_discrete_map=color_map,  # Menggunakan skema warna yang diurutkan
            labels={value_column: value_column},
            # text=value_column
        )

    # Update layout peta
    fig.update_geos(fitbounds="locations", visible=False)
    
    fig.update_layout(
        mapbox_style="carto-positron",  
        mapbox_zoom=6.5,  
        mapbox_center={"lat": 0.091, "lon": 102.349}, 
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )

    # Tampilkan visualisasi
    st.plotly_chart(fig, use_container_width=True)

