import streamlit as st
import pandas as pd
import pydeck as pdk
from database.db import fenologikDb
from database.models import Observations, Taxa
from streamlit_functions.visualisation_functions import create_layers, create_pydeck_chart #Use these to create dynamic map further down.
import os

#############################
#  - Database connection -  #
#############################

db = fenologikDb(os.environ['DATABASE_URL'])

#########################
#  - Filter handling -  #
#########################

#Sets a default to the session_state in cases of it being empty, such as first run. 
# Could be changed to do the 100 most recent observations of any art, to have a starting visualisation
results = getattr(st.session_state, 'results', []) 

species_list = db.get_unique_species_for_dropdown_test(Taxa)
#search_term = st.text_input("Sök art")
#filtered_species = [s for s in species_list if search_term.lower() in s.lower()]
selected_species = st.selectbox("Välj art", options=species_list)

start_date = st.date_input('Välj Startdatum')
end_date = st.date_input('Välj Slutdatum')

if st.button('Uppdatera filter'):
    filters = []

    if selected_species:
        taxonid = db.get_taxon_id(selected_species)
        species_filter = Observations.taxonId == taxonid
        filters.append(species_filter)

    if start_date:
        start_date_filter = Observations.startDate >= start_date
        filters.append(start_date_filter)

    if end_date:
        end_date_filter = Observations.endDate <= end_date
        filters.append(end_date_filter)

    # Uses filters to query the database and create a dataframe to be used in visualisations. Saves in a session_state
    st.session_state.results = db.observations_in_df(Observations, filters=filters)

###########################################
#  - Initializations of visualizations -  #
###########################################

zoom_level = st.slider('Välj Zoom Nivå', min_value=1, max_value=20, value=10) #Gotta play with these values a bit to get it right.

if hasattr(st.session_state, 'results') and not st.session_state.results.empty:
    layers = create_layers(st.session_state.results, opacity=0.2, zoom_level=zoom_level)
else:
    layers = None

st.pydeck_chart(create_pydeck_chart(layers))