import urllib.request, json
import pandas as pd
from database.db import fenologikDb
import os

##############################################################
### Functions for collecting observation data from SOS API ###
##############################################################

# CHANGE: Function to update database with new observations
def get_observations():
    try:
        # Change it so the parameters are passed in as arguments instead of in the url
        # take=100&sortOrder=Asc&validateSearchFilter=true&translationCultureCode=sv-SE&sensitiveObservations=false
        url = "https://api.artdatabanken.se/species-observation-system/v1/Observations/Search?skip=0&take=1000&sortOrder=Asc&validateSearchFilter=true&translationCultureCode=sv-SE&sensitiveObservations=false"

        # Request headers
        hdr ={
            'X-Api-Version': '1.5',
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache',
            'Ocp-Apim-Subscription-Key': os.environ['API_KEY'],
            # 'take': '1000'
        }

        # Request body
        data = {
            "output": {
                "fields": [
                    "taxon.id",
                    "event.startDate",
                    "event.endDate",
                    "location.decimalLatitude",
                    "location.decimalLongitude"
                ]
            },
            "date": {
                "startDate": "2023-01-01",
                "endDate": "2023-12-31",
                "dateFilterType": "OverlappingStartDateAndEndDate",
            },
            "taxon": {
                "includeUnderlyingTaxa": True,
                "ids": [4000104],
            }
        }
        data = json.dumps(data)
        # req = urllib.request.Request(url, headers=hdr, data = bytes(data.encode("utf-8")))
        req = urllib.request.Request(url, headers=hdr)
        req.get_method = lambda: 'POST'

        # Send HTTP request and load response into pandas dataframe
        response = urllib.request.urlopen(req)
        return response
    except Exception as e:
        print(e)

def transform_observations(json_data, table_name, file_name):
    try:
        df = pd.read_json(json_data)
        df = pd.json_normalize(df['records'], max_level=1)
        # CHANGE: File path when populating with whole dataset
        df.to_csv(file_name, index=False)
    except Exception as e:
        print(e)

# CHANGE: Function name
def populate_database():
    try:
        db = fenologikDb(os.environ['DATABASE_URL'])
        session = db.get_session()
        conn = session.connection().connection
        cur = conn.cursor()

        # CHANGE: File path when populating with whole dataset
        with open('testing/observations.csv', 'r') as f:
            next(f) # Skip the header row.
            cur.copy_from(f, 'observations', columns=('startDate', 'endDate', 'latitude', 'longitude', 'taxonId'), sep=',')
            conn.commit()

        session.close()
    except Exception as e:
        print(e)


#####################################################
### Add function for updating taxon list from API ###
#####################################################