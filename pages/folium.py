import streamlit as st
import folium
from streamlit_folium import st_folium, folium_static


m = folium.Map(location=[61.953, 14.816], zoom_start=4)
folium.Marker(
    [61.953, 14.816], popup="Liberty Bell", tooltip="Liberty Bell"
).add_to(m)

# call to render Folium map in Streamlit
st_data = st_folium(m, width=750)

