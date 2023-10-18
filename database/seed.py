import pandas as pd
import json
import urllib.request
import zipfile
import io
from sqlalchemy import create_engine # MetaData, Table, Column, Integer, String
import os

def observations_export(csv_save_path):
    try:
        # Change it so the parameters are passed in as arguments instead of in the url
        url = 'https://api.artdatabanken.se/species-observation-system/v1/Exports/Download/Csv?outputFieldSet=Minimum&validateSearchFilter=true&propertyLabelType=PropertyPath&cultureCode=sv-SE&gzip=true&sensitiveObservations=false'

        # Request headers
        hdr ={
            'X-Api-Version': '1.5',
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache',
            'Ocp-Apim-Subscription-Key': os.environ['API_KEY'],
            # 'take': '1000'
        }

        # Request body
        body = {
            "Output": {
                "Fields": [
                    "Occurrence.OccurrenceId",
                    "Taxon.Id",
                    "Event.StartDate",
                    "Event.EndDate",
                    "Location.DecimalLatitude",
                    "Location.DecimalLongitude"
                ]
            },
            "date": {
                "startDate": "2023-01-01",
                "endDate": "2023-01-31",
                "dateFilterType": "OverlappingStartDateAndEndDate"
            },
            "taxa": {
                "ids": [4000104],
                "includeUnderlyingTaxa": True
            }
        }
        # save_path = '/testing/medium_observations.csv'
        req = urllib.request.Request(url, headers=hdr, data=bytes(json.dumps(body).encode("utf-8")))
        req.get_method = lambda: 'POST'

        with urllib.request.urlopen(req) as response:
            data = response.read()

        with zipfile.ZipFile(io.BytesIO(data)) as z:
            z.extractall(csv_save_path)
        # data = json.dumps(data)
        # req = urllib.request.Request(url, headers=hdr, data = bytes(data.encode("utf-8")))
        # req.get_method = lambda: 'POST'

        # # Send HTTP request and load response into pandas dataframe
        # response = urllib.request.urlopen(req)
        # return response
    except Exception as e:
        print(e)

# def transform_observations():
#     try:
#         df = pd.read_json(get_observations())
#         df = pd.json_normalize(df['records'], max_level=1)
#         df.to_csv('testing/observations.csv', index=False)
#     except Exception as e:
#         print(e)

# def populate_database():
#     try:
#         db = fenologikDb(os.environ['DATABASE_URL'])
#         session = db.get_session()
#         conn = session.connection().connection
#         cur = conn.cursor()

#         # CHANGE: File path when populating with whole dataset
#         with open('testing/observations.csv', 'r') as f:
#             next(f) # Skip the header row.
#             cur.copy_from(f, 'observations', columns=('startDate', 'endDate', 'latitude', 'longitude', 'taxonId'), sep=',')
#             conn.commit()

#         session.close()
#     except Exception as e:
#         print(e)


# # get_observations
# transform_observations(get_observations(), 'records', 'testing/observations.csv')
# # get_taxa
# transform_observations(get_taxa(), 'natureConservationListTaxa', 'testing/taxon_list.json')

# # Retrieve taxon list from SOS API
# def taxon_list():
#     try:
#         url = "https://api.artdatabanken.se/taxonlistservice/v1/taxa"
        
#         hdr ={
#             # Request headers
#             'Content-Type': 'application/json',
#             'Cache-Control': 'no-cache',
#             'Ocp-Apim-Subscription-Key': os.environ['API_KEY'],
#             }

#         data = {
#             "conservationListIds": [245],
#             "outputFields": ["id", "scientificname", "swedishname", "englishname"]
#             }

#         data = json.dumps(data)
#         req = urllib.request.Request(url, headers=hdr, data = bytes(data.encode("utf-8")))
#         req.get_method = lambda: 'POST'
#         response = urllib.request.urlopen(req)
#         df = pd.read_json(response)

#         df.to_json('taxon_list.json', index=False)

#     except Exception as e:
#         print(e)

# # What is the name of the json file?
# data_file = 'testing/taxon_list.json'
# # What column contains the data dictionary?
# data_column = 'natureConservationListTaxa'
# # What dictionary key contains the data?
# data_key = 'taxonInformation'
# # What is the name of the table in the database?
# seed_table_name = 'taxa'


# # Exctract data from json file and return as pandas dataframe with normalized data
# df = pd.read_json(data_file)
# df[data_column] = df[data_column].apply(lambda x: json.loads(json.dumps(x)))
# df = pd.json_normalize(df[data_column], data_key)
# engine = create_engine(os.environ['DATABASE_URL'])

# # Send the DataFrame to database
# # Can't update existing table with overlapping data so we replace it instead, needs to be changed
# df.to_sql(seed_table_name, engine, if_exists='replace', index=False)

# print('Done!')