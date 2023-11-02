import streamlit as st
import pydeck as pdk
import geopandas as gpd
from sqlalchemy import create_engine
import os

# Create a database connection
engine = create_engine(os.environ['DATABASE_URL'])

# Load the grid data from PostGIS
grid_data = gpd.read_postgis('SELECT * FROM grid', engine, geom_col='geom')

# Convert the GeoDataFrame to a format that Pydeck understands
grid_data['lng'] = grid_data['geom'].centroid.x
grid_data['lat'] = grid_data['geom'].centroid.y

# Define the grid layer
grid_layer = pdk.Layer(
    "GridLayer",
    data=grid_data,
    get_position='[lng, lat]',
    pickable=True,
    extruded=True,
)

# Create a deck object
deck = pdk.Deck(
    layers=[grid_layer],
    initial_view_state=pdk.ViewState(
        latitude=59.334591,  # Coordinates of Stockholm, replace with your desired location
        longitude=18.063240,
        zoom=11,
        pitch=50,
    ),
)

# Display the map in Streamlit
st.pydeck_chart(deck)