import streamlit as st
import pandas as pd
import plotly.express as px

# Judul Aplikasi
st.title("Scatter Plot Visualisasi dengan Data Excel")

# Upload File Excel
uploaded_file = st.file_uploader("Upload file Excel Anda", type=["xlsx", "xls"])

if uploaded_file:
    # Load Data
    df = pd.read_excel(uploaded_file)
    st.write("Data yang diunggah:")
    st.write(df.head())

    # Pilih Kolom Long, Lat, dan Color
    st.sidebar.header("Konfigurasi Scatter Plot")
    long_column = st.sidebar.selectbox("Pilih kolom Longitude:", df.columns)
    lat_column = st.sidebar.selectbox("Pilih kolom Latitude:", df.columns)
    color_column = st.sidebar.selectbox("Pilih kolom untuk Color:", df.columns)

    # Opsi untuk Size (Optional)
    size_column = st.sidebar.selectbox("Pilih kolom untuk Size (Opsional):", ['None'] + list(df.columns))
    
    # Hover Data
    hover_columns = st.sidebar.multiselect("Pilih kolom tambahan untuk Hover:", df.columns)

    # Tentukan Tipe Data Color
    value_type = st.sidebar.radio("Tipe kolom Color:", ['Numerik', 'Kategori'], horizontal=True)

    # Pengaturan Warna
    if value_type == 'Numerik':
        color_option = st.radio("Pilih jenis skema warna:", ['Predefined', 'Custom'], horizontal=True)
        
        if color_option == 'Custom':
            st.write("Atur rentang warna:")
            ranges = []
            colors = []
            num_ranges = st.number_input("Jumlah rentang warna:", min_value=2, max_value=10, value=3, step=1)
            
            for i in range(num_ranges):
                col1, col2 = st.columns([1, 2])
                with col1:
                    point = st.number_input(f"Titik rentang {i+1} (0.0 - 1.0):", min_value=0.0, max_value=1.0, value=i/(num_ranges-1), key=f'point_{i}')
                with col2:
                    color = st.color_picker(f"Pilih warna untuk rentang {point:.2f}:", '#008000' if i == 0 else '#FF0000', key=f'color_{i}')
                ranges.append(point)
                colors.append(color)
            
            # Skema warna final
            color_scale = [[point, color] for point, color in zip(ranges, colors)]
        else:
            # Predefined Skema Warna
            predefined_color_scale = st.selectbox("Pilih skema warna pre-defined:",
                                                  ['Viridis', 'RdYlGn', 'Blues', 'Cividis', 'Inferno', 'Magma'])

    elif value_type == 'Kategori':
        # Warna untuk kategori
        unique_categories = df[color_column].unique().tolist()
        color_map = {}
        st.write("Atur warna untuk setiap kategori:")
        for category in unique_categories:
            color = st.color_picker(f"Pilih warna untuk '{category}'", '#d73027')
            color_map[category] = color

    # Filter data (konversi numerik jika perlu)
    filtered_df = df.copy()
    if value_type == 'Numerik':
        filtered_df[color_column] = pd.to_numeric(filtered_df[color_column], errors='coerce')
        filtered_df = filtered_df.dropna(subset=[color_column])

    # Kolom ukuran
    size_arg = None if size_column == 'None' else size_column

    # Plot Scatter
    st.subheader("Hasil Visualisasi Scatter Plot")
    if value_type == 'Numerik':
        fig = px.scatter_mapbox(
            filtered_df,
            lat=lat_column,
            lon=long_column,
            color=color_column,
            size=size_arg,
            color_continuous_scale=color_scale if color_option == 'Custom' else predefined_color_scale,
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

    # Layout Mapbox
    fig.update_layout(
        mapbox_style="open-street-map",
        margin={"r":0,"t":0,"l":0,"b":0}
    )

    st.plotly_chart(fig)
