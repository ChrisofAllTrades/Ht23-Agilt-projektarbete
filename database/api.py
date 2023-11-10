from datetime import datetime
import io
import json
import os
from urllib import error, parse, request 
import zipfile

from dateutil.relativedelta import relativedelta
import pandas as pd

from database.db import FenologikDb

# To do: Add function for updating taxon list from API (what interval?)
# To do Add function for updating observations from API (what interval?)
#     - It seems like some days include more than 25 000 observations (maximum allowed by obs_export_download function),
#       maybe use TimeRangeDto[Morning , Forenoon , Afternoon , Evening , Night]? Uses more up-to-date data and removes risk of overlapping requests 

class API:
    # Authorization token request
    # NOT BEST PRACTICE: Change to use client credentials flow instead of password flow
    # FIX: Doesn't work. Need client_id and client_secret from ArtDatabanken
    # @staticmethod
    # def auth_token():
    #     # The URL of the token endpoint
    #     token_url = "https://ids.artdatabanken.se/connect/token"

    #     # The data to send in the request
    #     data = {
    #         "grant_type": "password",
    #         "username": os.getenv("ART_USERNAME"),
    #         "password": os.getenv("ART_PASSWORD"),
    #         "client_id": "artdatabanken",
    #         "client_secret": os.getenv("ART_CLIENT_SECRET"),
    #         "scope": "openid"
    #     }
    #     # Encode the data
    #     data = parse.urlencode(data).encode()

    #     # Create the request
    #     req = request.Request(token_url, data=data)

    #     try:
                
    #         # Send the request and get the response
    #         with request.urlopen(req) as response:
    #             # Read the response
    #             response_data = response.read()
    #     except error.HTTPError as error:
    #         # If an HTTP error occurs (such as a 404 or 403) the error code and description are returned
    #         print(f"HTTP error: {error.code}")
    #         print(f"HTTP error: {error.read()}")
        
    #     # Parse the JSON response
    #     token_response = json.loads(response_data)

    #     # Extract the bearer token from the response
    #     bearer_token = token_response["access_token"]

    #     # Print the bearer token
    #     return bearer_token

    # Default dates for API calls
    endDate = datetime.today().date()
    startDate = endDate - relativedelta(days=1)

    # Converted to string to work with request body
    endDateStr = endDate.strftime("%Y-%m-%d")
    startDateStr = startDate.strftime("%Y-%m-%d")
    
    # Header for API calls
    # Authorization token only needed when running seed_Db.obs_query_loop()
    hdr = {
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache',
        #'Ocp-Apim-Subscription-Key': os.environ['API_KEY'],
    }

    # Body for API calls
    body = {
        "output": {
            "fields": [
            "occurrence.occurrenceId",
            "occurrence.organismQuantityInt",
            "taxon.id",
            "event.startDate",
            "event.endDate",
            ]
        },
        # All data providers that have bird observations (listed here: https://github.com/biodiversitydata-se/SOS/blob/master/Docs/DataProviders.md)
        "dataProvider": {
            "ids": [1, 9, 18, 19, 20, 21, 22, 23]
        },
        "date": {
            "startDate": startDateStr,
            "endDate": endDateStr
        },
        "taxon": {
            "includeUnderlyingTaxa": True,
            "ids": [4000104] # Aves (birds)
        }
    }



    # Outputs the number of observations for a given search filter
    def obs_count(body):
        url = ("https://api.artdatabanken.se/species-observation-system/v1/Observations/Count"
               "?validateSearchFilter=true"
               "&sensitiveObservations=false")
            
        req = request.Request(url, headers=API.hdr, data=bytes(json.dumps(body).encode("utf-8")))
        req.get_method = lambda: "POST"

        with request.urlopen(req) as response:
            data = response.read()
            count = data.decode("utf-8")
            print(count)
            return int(count)
    


    # Outputs the total number of observations for each data provider
    def dataProvider_obs_count():
        # Loop through data providers 1-24 (listed here: https://github.com/biodiversitydata-se/SOS/blob/master/Docs/DataProviders.md)
        for i in [1, 9, 18, 19, 20, 21, 22, 23]:
            # Request body
            body_count = {
                "dataProvider": {
                    "ids": [i]
                },
                "date": {
                    "startDate": datetime(1600, 1, 1).strftime("%Y-%m-%d"),
                    "endDate": datetime.today().date().strftime("%Y-%m-%d")
                }
            }
            
            API.body.update(body_count)

            print(f"Number of observations in data provider {i}:")
            API.obs_count(API.body)

##############################################################
### Functions for collecting observation data from SOS API ###
##############################################################

    # Queries endpoint for observations and returns a pandas dataframe
    # 1 000 observations max per call
    # CHANGE: Function to update database with new observations
    def get_observations():
        url = ("https://api.artdatabanken.se/species-observation-system/v1/Observations/Search"
                "?skip=0"
                "&take=10"
                "&sortOrder=Asc"
                "&validateSearchFilter=true"
                "&translationCultureCode=sv-SE"
        )

        req = request.Request(url, headers=API.hdr, data=bytes(json.dumps(API.body).encode("utf-8")))
        req.get_method = lambda: "POST"

        # # Set the display options
        # pd.set_option('display.max_rows', None)
        # pd.set_option('display.max_columns', None)
        # pd.set_option('display.width', None)
        # pd.set_option('display.max_colwidth', None)

        # Send HTTP request and load response into pandas dataframe
        response = request.urlopen(req)
        return response
        # print(pd.read_json(response))



    # Transforms response from get_observations() into a pandas dataframe and saves it as a CSV file
    # FIX: Doesn't work properly (only adds columns with empty values)
    def transform_observations(json_data, column, file_name):
        df = pd.read_json(json_data)
        print(df)
        # Normalizes column containing the wanted data
        df = pd.json_normalize(df[column], max_level=1)
        df.to_csv(file_name, index=False)
        


    # Uses Exports_DownloadGeoJson operation of the SOS API to download observations as GeoJson
    # 25 000 observations max per call, throws error 400 if exceeded
    def obs_export_download(geojson_save_directory):
        url = ("https://api.artdatabanken.se/species-observation-system/v1/Exports/Download/GeoJson"
               "?validateSearchFilter=true"
               "&cultureCode=sv-SE"
               "&gzip=true"
        )

        req = request.Request(url, headers=API.hdr, data=bytes(json.dumps(API.body).encode("utf-8")))
        req.get_method = lambda: "POST"

        with request.urlopen(req) as response:
            data = response.read()

        with zipfile.ZipFile(io.BytesIO(data)) as z:
            z.extractall(geojson_save_directory)

##################################################
### Functions for updating taxon list from API ###
##################################################

    def get_taxa():
        url = ("https://api.artdatabanken.se/taxonlistservice/v1/taxa")
        
        body = {
            "conservationListIds": [245],
            "outputFields": [
                "id", 
                "scientificname", 
                "swedishname", 
                "englishname"
            ]
        }

        req = request.Request(url, headers=API.hdr, data=bytes(json.dumps(body).encode("utf-8")))
        req.get_method = lambda: "POST"

        with request.urlopen(req) as response:
            data = response.read()
            data_json = json.loads(data)

        with open("taxa.json", "w") as file:
            json.dump(data_json, file, indent=4)