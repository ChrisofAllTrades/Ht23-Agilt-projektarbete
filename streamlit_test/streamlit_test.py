import streamlit as st
import pydeck as pdk

# Define the initial view
view_state = pdk.ViewState(
    latitude=63,
    longitude=15,
    zoom=3.5
)

# Define the base map TileLayer
map_layer = pdk.Layer(
    "TileLayer",
    data=None,
    get_tile_data="https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png",
    pickable=False,
    auto_highlight=True,
    get_fill_color=[255, 165, 0],
    get_line_color=[0, 0, 0],
)

# Define the grid layer
grid_layer = pdk.Layer(
    "MVTLayer",
    # data="http://localhost:3000/obs_count_by_taxon_and_date/{z}/{x}/{y}?query_params={\"taxon_id\":102991,\"start_date\":\"2023-01-01\",\"end_date\":\"2023-11-08\"}",
    # data="http://localhost:3000/get_square_grid/{z}/{x}/{y}",
    data="http://localhost:3000/square_grid_function/{z}/{x}/{y}",
    # data="http://0.0.0.0:7800/square_grid_function/{z}/{x}/{y}.pbf",
    # data="http://0.0.0.0:7800/public.square_grid/{z}/{x}/{y}.pbf",
    pickable=True,
    auto_highlight=True,
    # get_fill_color="[255, properties.obs_count / 25 * 255, 0]",
    get_fill_color="[128, 50, 128, (properties.obs_count / 43.5) + 1]",
    getLineColor="[128, 50, 128, (properties.obs_count / 43.5) + 5]",
    lineWidthMinPixels=1,
    # onTileLoad=lambda tile: st.write(f"Loaded tile {tile.x}/{tile.y}/{tile.z}"),
)

# Render the map with both layers
r = pdk.Deck(layers=[map_layer, grid_layer], initial_view_state=view_state)
st.pydeck_chart(r)