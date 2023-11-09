import streamlit as st
from datetime import datetime
from database.models import Taxa
from streamlit_functions.visualisation_functions import get_grid_layer
import pydeck as pdk
import os

from database.db import FenologikDb

db = FenologikDb(os.environ['DATABASE_URL'])

#######################################
#  - Initial viewstate and filters -  #
#######################################

grid_layer = get_grid_layer("http://localhost:7800/public.square_grid/{z}/{x}/{y}.pbf") #Byt ut med tileserv funktion url.

view_state = pdk.ViewState(
    latitude=61.953,
    longitude=14.816,
    zoom=3.5,
    min_zoom=3.5,
    max_zoom=16,
)

species_list = db.get_unique_species_for_dropdown(Taxa)
map_placeholder = st.empty()

with st.form("filters_form"):
    species = st.selectbox("Select species", species_list)
    startdate = st.date_input("Start Date")
    enddate = st.date_input("End Date")
    submitted = st.form_submit_button("Submit")

if submitted:
    list_of_filters = [db.get_taxon_id(species), startdate, enddate]
    st.write(list_of_filters)
    #Here we should send the data (list_of_filters) to the database function.
    #In order to do an animation we need to iterate through objects, and or update the layer structure(?)

#st.write(startdate)
#st.write(enddate)
#st.write(db.get_taxon_id(species))

####################################
#  - Deck and map initialization-  #
####################################

deck = pdk.Deck(
    initial_view_state=view_state,
    layers=[grid_layer],
    map_style="mapbox://styles/mapbox/outdoors-v12",
)

map_placeholder.pydeck_chart(deck)

#Put in the map and deck down here in case we need to resort to some way of creating the map with the data from the form -> db functions -> map.



