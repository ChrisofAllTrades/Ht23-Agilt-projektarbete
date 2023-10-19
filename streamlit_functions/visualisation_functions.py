import pydeck as pdk
import streamlit as st
import json


##################################################
#  - Functions for map visualisation creation -  #
##################################################

#Todo: Look into more visualizations that we can create based off of the data that is prevalent.
#Todo: Create a function that converts the necessary data points into a suitable dataframe <- we need this, do it from db.py then convert into df of appropriate size and cache?
#Todo: define a color range for the grids.


def create_layers(df, opacity, zoom_level):
    with open("swedish_regions.json") as f:
        geojson_data = json.load(f)

    def calculate_cell_size(zoom_level):
        return max(1000 / (zoom_level / 10), 50)
    
    cell_size_pixels = calculate_cell_size(zoom_level)

    def masking_layer(geojson_data):
        return pdk.Layer(
        "GeoJsonLayer",
        data=geojson_data,
        opacity=0,
        get_fill_color="[255, 255, 255, 180]",
        get_line_color=[255, 255, 255],
        pickable=False,
        visible=False, 
        )

    def create_screengrid_layer(df, opacity, cell_size_pixels):
        return pdk.Layer(
        "ScreenGridLayer",
        data=df,      
        pickable=False,
        opacity=opacity,
        cell_size_pixels=cell_size_pixels, 
        color_range=[
            [], 
            [],
            [],
            [],
            [],
            [],
        ],
        get_position='[longitude, latitude]',
        )
    
    def create_tooltip_layer(df, cell_size):
        return pdk.Layer(
        "GridLayer",
        data=df,
        opacity=0,
        get_position='[longitude, latitude]',
        pickable=True, 
        extruded=False,
        cell_size=cell_size,
        #tooltip="cellWeight",  # Which column to display on hover.
        )
        
    geojson_layer = masking_layer(geojson_data)
    screengrid_layer = create_screengrid_layer(df, opacity, cell_size_pixels)
    tooltip_layer = create_tooltip_layer(df, calculate_cell_size(zoom_level))

    return geojson_layer, screengrid_layer, tooltip_layer

def create_pydeck_chart(layers):
    return pdk.Deck(
    layers=[layers],
    initial_view_state=pdk.ViewState(
        latitude=65,
        longitude=17,
        zoom=3.5,
        pitch=0,
    )
)