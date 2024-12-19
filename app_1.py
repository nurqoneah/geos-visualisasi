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
        with open(".\\geos\\DESA\\Desa NOP Pekanbaru.geojson") as file_json:
            return json.load(file_json)
    elif geo_level == "Kecamatan":
        with open(".\\geos\\KECAMATAN\\kecamatan nop pekanbaru.geojson") as file_json:
            return json.load(file_json)

# Fungsi untuk memilih kolom
def select_column(label, df):
    return st.selectbox(f"Pilih kolom untuk {label}:", df.columns)

# Fungsi render untuk peta (Map)
def render_map(df, geojson_data, geo_column, value_column, value_type, color_option, predefined_color_scale, custom_colorscale, hover_data):
    # Visualisasi Peta
    if value_type == 'Numerik':
        fig = px.choropleth_mapbox(
            df,
            geojson=geojson_data,
            locations=geo_column,
            featureidkey=f"properties.DESA" if geo_level == 'Kelurahan' else f"properties.KECAMATAN",
            color=value_column,
            color_continuous_scale=custom_colorscale if color_option == 'Custom' else predefined_color_scale,
            range_color=(df[value_column].min(), df[value_column].max()),
            hover_data=hover_data,
            labels={value_column: value_column},
        )
    else:
        fig = px.choropleth_mapbox(
            df,
            geojson=geojson_data,
            locations=geo_column,
            featureidkey=f"properties.DESA" if geo_level == 'Kelurahan' else f"properties.KECAMATAN",
            color=value_column,
            color_discrete_map=color_map,
            hover_data=hover_data,
            labels={value_column: value_column},
        )
    
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_zoom=6.5,
        mapbox_center={"lat": 0.091, "lon": 102.349},
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )
    return fig

# Fungsi render untuk Scatter Plot
def render_scatter(df, long_column, lat_column, color_column, size_column, hover_columns, value_type, color_option, color_scale, size_max=15):
    if value_type == 'Numerik':
        fig = px.scatter_mapbox(
            df,
            lat=lat_column,
            lon=long_column,
            color=color_column,
            size=size_column,
            color_continuous_scale=color_scale,
            hover_data=hover_columns,
            size_max=size_max,
            zoom=5,
        )
    else:
        fig = px.scatter_mapbox(
            df,
            lat=lat_column,
            lon=long_column,
            color=color_column,
            size=size_column,
            hover_data=hover_columns,
            color_discrete_map=color_map,
            size_max=size_max,
            zoom=5,
        )
    
    fig.update_layout(
        mapbox_style="open-street-map",
        margin={"r":0, "t":0, "l":0, "b":0}
    )
    return fig

# Fungsi render untuk Line Plot
def render_line(df, col_lat_asal, col_lon_asal, col_lat_tujuan, col_lon_tujuan, color_column, size_column, hover_columns, color_type, default_size=2):
    fig = go.Figure()

    for i, row in df.iterrows():
        fig.add_trace(
            go.Scattermapbox(
                mode="lines",
                lat=[row[col_lat_asal], row[col_lat_tujuan]],
                lon=[row[col_lon_asal], row[col_lon_tujuan]],
                line=dict(width=2, color=row["color"]),
                marker=dict(size=row["size"]),
                hoverinfo="text",
                hovertext={col: row[col] for col in hover_columns}
            )
        )

    fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_zoom=6.5,
        mapbox_center={"lat": 0.091, "lon": 102.349},
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )
    return fig

def main():
    uploaded_file = st.file_uploader("Upload file CSV atau Excel", type=['csv', 'xlsx'])
    if uploaded_file:
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('csv') else pd.read_excel(uploaded_file)
        st.write("Data Preview:")
        st.dataframe(df)

        # Konfigurasi melalui Sidebar
        with st.sidebar:
            st.header("Konfigurasi Visualisasi")

            # Pilih jenis visualisasi
            visualizations = st.multiselect("Pilih Visualisasi:", ['Map', 'Scatter', 'Line'])

            if 'Map' in visualizations:
                geo_level = st.selectbox("Pilih tingkat wilayah:", ["Kelurahan", "Kecamatan"])
                geojson_data = load_geojson(geo_level)
                geo_column = select_column("Kolom wilayah (kelurahan/kecamatan):", df)
                value_column = select_column("Kolom nilai:", df)
                value_type = st.selectbox("Tipe data nilai:", ["Numerik", "Kategori"])

                # Warna
                color_option = st.radio("Pilih jenis skema warna:", ['Predefined', 'Custom'], horizontal=True)
                if color_option == 'Custom':
                    st.write("Atur rentang warna:")
                    custom_colorscale = []
                    num_ranges = st.number_input("Jumlah rentang warna:", min_value=1, max_value=10, value=3, step=1)
                    for i in range(num_ranges):
                        point = st.number_input(f"Titik rentang {i+1} (0.0 - 1.0):", min_value=0.0, max_value=1.0, value=i/(num_ranges-1), key=f'point_{i}')
                        color = st.color_picker(f"Pilih warna untuk rentang {point:.2f}:", '#008000' if i == 0 else '#FF0000', key=f'color_{i}')
                        custom_colorscale.append([point, color])
                else:
                    predefined_color_scale = st.selectbox("Pilih skema warna:", ['Viridis', 'RdYlGn', 'Blues', 'Cividis', 'Inferno', 'Magma'])

            if 'Scatter' in visualizations:
                long_column = st.sidebar.selectbox("Pilih kolom Longitude:", df.columns)
                lat_column = st.sidebar.selectbox("Pilih kolom Latitude:", df.columns)
                color_column = st.sidebar.selectbox("Pilih kolom untuk Color:", df.columns)
                size_column = st.sidebar.selectbox("Pilih kolom untuk Size (Opsional):", ['None'] + list(df.columns))
                hover_columns = st.sidebar.multiselect("Pilih kolom tambahan untuk Hover:", df.columns)
                value_type = st.sidebar.radio("Tipe kolom Color:", ['Numerik', 'Kategori'], horizontal=True)

            if 'Line' in visualizations:
                col_lat_asal = st.sidebar.selectbox("Kolom Latitude Asal", df.columns)
                col_lon_asal = st.sidebar.selectbox("Kolom Longitude Asal", df.columns)
                col_lat_tujuan = st.sidebar.selectbox("Kolom Latitude Tujuan", df.columns)
                col_lon_tujuan = st.sidebar.selectbox("Kolom Longitude Tujuan", df.columns)
                color_column = st.sidebar.selectbox("Kolom untuk Warna", df.columns)
                color_type = st.sidebar.radio("Tipe Data untuk Warna:", ["Numerik", "Kategori"], horizontal=True)
                size_column = st.sidebar.selectbox("Kolom untuk Ukuran Garis (Opsional)", ["None"] + list(df.columns))

        fig = go.Figure()

        # Render Map
        if 'Map' in visualizations:
            fig_map = render_map(df, geojson_data, geo_column, value_column, value_type, color_option, predefined_color_scale, custom_colorscale, hover_columns)
            fig.add_traces(fig_map.data)

        # Render Scatter Plot
        if 'Scatter' in visualizations:
            fig_scatter = render_scatter(df, long_column, lat_column, color_column, size_column, hover_columns, value_type, color_option, predefined_color_scale)
            fig.add_traces(fig_scatter.data)

        # Render Line Plot
        if 'Line' in visualizations:
            fig_line = render_line(df, col_lat_asal, col_lon_asal, col_lat_tujuan, col_lon_tujuan, color_column, size_column, hover_columns, color_type)
            fig.add_traces(fig_line.data)

        st.plotly_chart(fig)

if __name__ == "__main__":
    main()
