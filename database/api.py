import urllib.request, urllib.parse, json
import pandas as pd
import os
import io
from datetime import datetime
from dateutil.relativedelta import relativedelta
import zipfile
from database.db import fenologikDb

# To do: Add function for updating taxon list from API (what interval?)
# To do Add function for updating observations from API (what interval?)
#     - It seems like some days include more than 25 000 observations (maximum allowed by obs_export_download function),
#       maybe use TimeRangeDto[Morning , Forenoon , Afternoon , Evening , Night]? Uses more up-to-date data and removes risk of overlapping requests 
# To do: Observations need timestamp. Include in date column or add new column?

##############################################################
### Functions for collecting observation data from SOS API ###
##############################################################

class API:
    # Authorization token request
    # NOT BEST PRACTICE: Change to use client credentials flow instead of password flow
    # DOES NOT WORK: Need client_id and client_secret from ArtDatabanken
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
    #     data = urllib.parse.urlencode(data).encode()

    #     # Create the request
    #     req = urllib.request.Request(token_url, data=data)

    #     try:
                
    #         # Send the request and get the response
    #         with urllib.request.urlopen(req) as response:
    #             # Read the response
    #             response_data = response.read()
    #     except urllib.error.HTTPError as error:
    #         # If an HTTP error occurs (such as a 404 or 403) the error code and description are returned
    #         print(f"HTTP error: {error.code}")
    #         print(f"HTTP error: {error.read()}")
        
    #     # Parse the JSON response
    #     token_response = json.loads(response_data)

    #     # Extract the bearer token from the response
    #     bearer_token = token_response["access_token"]

    #     # Print the bearer token
    #     return bearer_token

    # Header for API calls
    # Authorization token only needed when running seed_Db.obs_query_loop()

    endDate = datetime.today().date()
#    startDate = endDate - relativedelta(months=1)
    startDate = datetime.today().date()

    endDateStr = endDate.strftime("%Y-%m-%d")
    startDateStr = startDate.strftime("%Y-%m-%d")
    
    hdr = {
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache',
        'Ocp-Apim-Subscription-Key': os.environ['API_KEY'],
        'Authorization': os.environ['AUTH_TOKEN'] # CHANGE: Append to seed_Db.obs_query_loop() hdr instead
    }

    body = {
        "output": {
            "fields": [
            "taxon.id",
            "event.startDate",
            "event.endDate",
            "location.Sweref99TmX",
            "location.Sweref99TmY"
            ]
        },
        "date": {
            "startDate": startDateStr,
            "endDate": endDateStr
        },
        "taxon": {
            "includeUnderlyingTaxa": True,
            "ids": [4000104]
        }
    }

    # Outputs the number of observations for a given search filter
    def obs_count(body):
        url = ("https://api.artdatabanken.se/species-observation-system/v1/Observations/Count"
               "?validateSearchFilter=true"
               "&sensitiveObservations=false")
            
        req = urllib.request.Request(url, headers=API.hdr, data=bytes(json.dumps(body).encode("utf-8")))
        req.get_method = lambda: "POST"

        with urllib.request.urlopen(req) as response:
            data = response.read()
            count = data.decode("utf-8")
            print(count)
            return int(count)

    # CHANGE: Function to update database with new observations
    def get_observations():
        url = ("https://api.artdatabanken.se/species-observation-system/v1/Observations/Search"
                "?skip=0"
                "&take=1000"
                "&sortOrder=Asc"
                "&validateSearchFilter=true"
                "&translationCultureCode=sv-SE"
                "&sensitiveObservations=false"
        )

        req = urllib.request.Request(url, headers=API.hdr, data=bytes(json.dumps(API.body).encode("utf-8")))
        req.get_method = lambda: 'POST'

        # Send HTTP request and load response into pandas dataframe
        response = urllib.request.urlopen(req)
        return response
        
    # Uses Exports_DownloadCsv operation of the SOS API to download observations as CSV
    #25 000 observations max per call, throws error 400 if exceeded
    def obs_export_download(csv_save_path):
        url = ("https://api.artdatabanken.se/species-observation-system/v1/Exports/Download/Csv"
               "?validateSearchFilter=true"
               "&propertyLabelType=PropertyPath"
               "&cultureCode=sv-SE"
               "&gzip=true"
               "&sensitiveObservations=false"
        )

        # save_path = '/testing/medium_observations.csv'
        req = urllib.request.Request(url, headers=API.hdr, data=bytes(json.dumps(API.body).encode("utf-8")))
        req.get_method = lambda: 'POST'

        # with urllib.request.urlopen(req) as response:
        #     data = response.read()

        response = urllib.request.urlopen(req)
        return response

        with zipfile.ZipFile(io.BytesIO(data)) as z:
            z.extractall(csv_save_path)

    def transform_observations(json_data, column, file_name):
        df = pd.read_json(json_data)
        df = pd.json_normalize(df[column], max_level=1)
        # CHANGE: File path when populating with whole dataset
        df.to_csv(file_name, index=False)

##################################################
### Functions for updating taxon list from API ###
##################################################