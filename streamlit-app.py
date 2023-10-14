import streamlit as st
import pandas as pd
import pydeck as pdk
import ast


file_path = 'data.csv'

def safe_literal_eval(value):
    try:
        return ast.literal_eval(value)
    except (SyntaxError, ValueError):
        return None


def get_data(file_path):
    #Prepares the "records" category into a dataframe to be used by our visualisations:
    df = pd.read_csv(file_path, header=None, names=['skip', 'take', 'totalCount', 'records'])
    df['records'] = df['records'].apply(safe_literal_eval)
    df = df.dropna(subset=['records'])
    df = pd.concat([df.drop(['records'], axis=1), df['records'].apply(pd.Series)], axis=1)
    
    #Start and end date into two different columns.
    df['start_date'] = df['event'].apply(lambda x: x['startDate'] if isinstance(x, dict) and 'startDate' in x else None)
    df['end_date'] = df['event'].apply(lambda x: x['endDate'] if isinstance(x, dict) and 'endDate' in x else None)

    # Extract 'latitude' and 'longitude' from the location column:
    df['latitude'] = df['location'].apply(lambda x: x['decimalLatitude'] if x is not None else None)
    df['longitude'] = df['location'].apply(lambda x: x['decimalLongitude'] if x is not None else None)

    #Extract taxon_id and vernacular_name from the taxon column::
    df['taxon_id'] = df['taxon'].apply(lambda x: x['id'] if x is not None else None)
    df['vernacular_name'] = df['taxon'].apply(lambda x: x['vernacularName'] if x is not None else None)

    #Defining datatypes for our columns (to_datetime doesn't really want to work atm):

    df['start_date'] = pd.to_datetime(df['start_date']) #Still an object without a datatype (?) and I don't know why.
    df['end_date'] = pd.to_datetime(df['end_date']) #Still an object without a datatype (?) and I don't know why.
    df['latitude'] = pd.to_numeric(df['latitude'].astype(float))
    df['longitude'] = pd.to_numeric(df['longitude'].astype(float)) 
    df['taxon_id'] = pd.to_numeric(df['taxon_id'])
    df['vernacular_name'] = df['vernacular_name'].astype(str) #Still an object and I don't know why.

    # Drop unnecessary columns
    df = df.drop(['skip', 'take', 'totalCount', 'event', 'location', 'taxon'], axis=1)
    return df


df = get_data(file_path)


coordinates_df = df[['latitude','longitude']]

heatmap_layer = pdk.Layer(
    'HeatmapLayer',
    data=coordinates_df,
    get_position=['longitude', 'latitude'],
    threshold=0.4,
)

st.pydeck_chart(pdk.Deck(
    map_style=None,
    initial_view_state=pdk.ViewState(
        latitude=65,
        longitude=17,
        zoom=3.5,
        pitch=0,
        ),
    layers=[heatmap_layer] 
))

st.write("Ovan visas en heatmap på dem 100 första observationerna av nötkråka i år.")

st.dataframe(df)

st.dataframe(coordinates_df)
st.dataframe(df.dtypes)

st.button("Rerun")