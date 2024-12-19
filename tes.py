import plotly.graph_objects as go
import pandas as pd

# Dataframe contoh
df_scatter = pd.DataFrame({
    'lat': [0.091, 0.092, 0.093],
    'long': [102.349, 102.350, 102.351],
    'site_id': ['Site1', 'Site2', 'Site3'],
    'category': ['circle', 'cross', 'bicycle'],
    'value': [10, 20, 30]
})

# Pilih kolom untuk menentukan ikon
icon_column = 'category'  # Menggunakan kolom kategori untuk ikon
color_column = 'value'  # Menggunakan kolom numerik untuk warna

# Mapping nilai unik ke ikon
unique_values = df_scatter[icon_column].unique()
icon_map = {value: value for value in unique_values}  # Mapping langsung

# Membuat peta
fig = go.Figure()

# Menambahkan scatter points dengan ikon dan warna
for value, icon in icon_map.items():
    filtered_data = df_scatter[df_scatter[icon_column] == value]
    
    fig.add_trace(go.Scattermapbox(
        lat=filtered_data['lat'],
        lon=filtered_data['long'],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=15,
            symbol=icon,  # Ikon sesuai dengan kategori (bus, airport, dsb.)
            color=filtered_data[color_column],  # Skala warna berdasarkan kolom numerik
            colorscale='Viridis',  # Skema warna untuk numerik
            showscale=True
        ),
        text=filtered_data['site_id'],  # Menampilkan ID pada hover
        name=str(value)  # Menambahkan nama pada legend
    ))

# Mengatur layout peta
fig.update_layout(
    mapbox_style="carto-positron",
    mapbox_zoom=6.5,
    mapbox_center={"lat": 0.092, "lon": 102.350},
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
)

# Menampilkan peta
fig.show()
