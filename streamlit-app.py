import streamlit as st
import requests

#########################
#  - Filter handling -  #
#########################

if st.button('Download Tiles'):
    try:
        response = requests.get('http://127.0.0.1:5000/populate_tiles_table')
        if response.status_code == 200:
            st.success('Tiles acquired successfully and merged with database!')
        else:
            st.error('An error occured when downloading the tiles :(')
    except requests.exceptions.RequestException as e:
        st.error(f'Request failed: {e}')

###########################################
#  - Initializations of visualizations -  #
###########################################

