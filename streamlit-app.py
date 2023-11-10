import streamlit as st
from database.models import Taxa
from streamlit_functions.visualisation_functions import get_grid_layer, get_date_from_string, get_daily_data, get_daily_urls, get_weekly_data, get_weekly_urls
import pydeck as pdk
import os
import datetime

from database.db import FenologikDb

db = FenologikDb(os.environ['DATABASE_URL'])

#######################################
#  - Initial viewstate and filters -  #
#######################################

st.set_page_config(layout="wide")

query_params = st.experimental_get_query_params()
if 'day' in query_params:
    # Set the current day based on the query parameter
    st.session_state['current_day'] = int(query_params['day'][0])
else:
    # If 'day' is not in query parameters, initialize it to 0 and set the query parameter
    st.session_state['current_day'] = 0
    st.experimental_set_query_params(day=0)

st.sidebar.header("Date Range Navigation")

def update_map(grid_layer):
    view_state = pdk.ViewState(
        latitude=61.953,
        longitude=14.816,
        zoom=3.5,
        min_zoom=3.5,
        max_zoom=16,
    )

    deck = pdk.Deck(
        initial_view_state=view_state,
        layers=[grid_layer],
        map_style="mapbox://styles/mapbox/outdoors-v12",
    )

    return deck

if 'filters' not in st.session_state:
    st.session_state['filters'] = [102966, datetime.date(2023, 10, 1), datetime.date(2023, 11, 1)]

species_list = db.get_unique_species_for_dropdown(Taxa)
map_placeholder = st.empty()

query_params = st.experimental_get_query_params()
if 'day' in query_params:
    day_index = int(query_params['day'][0])
    st.session_state['current_day'] = day_index

with st.form("filters_form"):
    species = st.selectbox("Select species", species_list)
    startdate = st.date_input("Start Date")
    enddate = st.date_input("End Date")
    submitted = st.form_submit_button("Submit")

if submitted:
    list_of_filters = [db.get_taxon_id(species), startdate, enddate]
    st.session_state["filters"] = list_of_filters
    st.write(st.session_state["filters"])


if 'filters' in st.session_state:
    # Unpack the session state values
    species_id, start_date_str, end_date_str = st.session_state['filters']
    # Convert string dates to datetime.date objects if they are string dates (returns datetime.date object otherwise)
    start_date = get_date_from_string(start_date_str)
    end_date = get_date_from_string(end_date_str)
    
    weekly_data = get_weekly_data(species_id, start_date, end_date)
    weekly_urls = get_weekly_urls(weekly_data)

    total_weeks = ((end_date - start_date).days // 7) + 1
    st.sidebar.write(f"**Date Range:** {start_date_str} -> {end_date_str}")
    st.sidebar.write(f"**Total Weeks:** {total_weeks} week(s)")

    if 'current_week' not in st.session_state or 'week' in query_params:
        st.session_state['current_week'] = 0 if 'week' not in query_params else int(query_params['week'][0])

    week_being_viewed = st.sidebar.container()

    prev_col, next_col = st.sidebar.columns(2)
    with prev_col:
        if st.button('Previous Week'):
            st.session_state['current_week'] = max(0, st.session_state['current_week'] - 1)
            st.experimental_set_query_params(week=st.session_state['current_week'])

    with next_col:
        if st.button('Next Week'):
            st.session_state['current_week'] = min(total_weeks - 1, st.session_state['current_week'] + 1)
            st.experimental_set_query_params(week=st.session_state['current_week'])
    

    ####################################
    #  - Deck and map initialization-  #
    ####################################


# Use the current day index to get the URL for the grid layer
if 'current_week' in st.session_state and weekly_urls:
    current_url = weekly_urls[st.session_state['current_week']]
    current_week_data = weekly_data[st.session_state['current_week']]
    start_date_current_week = current_week_data['start_date']
    end_date_current_week = current_week_data['end_date']
    week_being_viewed.write(f"**Date range being viewed:** {start_date_current_week} - {end_date_current_week}")
    grid_layer = get_grid_layer(current_url)
    deck = update_map(grid_layer)
    map_placeholder.pydeck_chart(deck)





