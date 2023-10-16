import urllib.request, json
import pandas as pd
import os

##############################################################
### Functions for collecting observation data from SOS API ###
##############################################################

def get_observations():
    try:
        # Change it so the parameters are passed in as arguments instead of in the url
        # take=100&sortOrder=Asc&validateSearchFilter=true&translationCultureCode=sv-SE&sensitiveObservations=false
        url = "https://api.artdatabanken.se/species-observation-system/v1/Observations/Search"

        # Request headers
        hdr ={
            'X-Api-Version': '1.5',
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache',
            'Ocp-Apim-Subscription-Key': os.environ['API_KEY'],
            'take': '100',
        }

        # Request body
        data = {
            "output": {
                "fields": [
                    "taxon.vernacularName", 
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
        req = urllib.request.Request(url, headers=hdr, data = bytes(data.encode("utf-8")))

        req.get_method = lambda: 'POST'

        # Send HTTP request and load response into pandas dataframe
        response = urllib.request.urlopen(req)
        df = pd.read_json(response)

        # Save pandas dataframe to json
        ### Chage this to post to database instead of saving to file ###
        df.to_json('obesrvations.json', index=False)
    except Exception as e:
        print(e)


####################################################
### Add function for getting taxon list from API ###
####################################################