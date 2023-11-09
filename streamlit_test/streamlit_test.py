import streamlit as st
import pydeck as pdk

# Define the initial view
view_state = pdk.ViewState(
    latitude=63,
    longitude=15,
    zoom=3.5
)

def click_callback(info):
    if info is not None and 'object' in info and info['object'] is not None:
        tile_id = info['object'].get('id', 'No id')
        st.write(f'Tile id: {tile_id}')

# Define the base map TileLayer
map_layer = pdk.Layer(
    "TileLayer",
    data=None,
    get_tile_data="https://a.tile.openstreetmap.org/{z}/{x}/{y}.png",
    pickable=False,
    auto_highlight=True,
    get_fill_color=[255, 165, 0],
    get_line_color=[0, 0, 0],
)

# Define the grid layer
grid_layer = pdk.Layer(
    "MVTLayer",
    data="http://localhost:3000/square_grid_obs_count/{z}/{x}/{y}",
    pickable=True,
    auto_highlight=True,
    get_fill_color="[255, properties.obs_count / 25 * 255, 0]",
    getLineColor=[0, 0, 0],
    lineWidthMinPixels=1,
)

# Render the map with both layers
r = pdk.Deck(layers=[map_layer, grid_layer], initial_view_state=view_state)
st.pydeck_chart(r)