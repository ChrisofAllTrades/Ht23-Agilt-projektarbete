import urllib.request, json
import pandas as pd
import os

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
        df.to_json('testing/observations.json', index=False)
    except Exception as e:
        print(e)

get_observations()
print('Done!')

def test_query():
    try:
        url = "https://api.artdatabanken.se/species-observation-system/v1/Observations/Search?skip=0&take=100&sortOrder=Asc&validateSearchFilter=true&translationCultureCode=sv-SE&sensitiveObservations=false"

        # Request headers
        hdr ={
        'X-Api-Version': '1.5',
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache',
        'Ocp-Apim-Subscription-Key': os.environ['API_KEY'],
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
                "ids": [100090, ],
            }
        }
        data = json.dumps(data)
        req = urllib.request.Request(url, headers=hdr, data = bytes(data.encode("utf-8")))

        req.get_method = lambda: 'POST'

        # Send HTTP request and load response into pandas dataframe
        response = urllib.request.urlopen(req)
        df = pd.read_json(response)

        # Save pandas dataframe to json
        df.to_json('obesrvations.json', index=False)
    except Exception as e:
        print(e)

def taxon_list():
    try:
        url = "https://api.artdatabanken.se/taxonlistservice/v1/taxa"
        
        hdr ={
            # Request headers
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache',
            'Ocp-Apim-Subscription-Key': os.environ['API_KEY'],
            }

        data = {
            "conservationListIds": [245],
            "outputFields": ["id", "scientificname", "swedishname", "englishname"]
            }

        data = json.dumps(data)
        req = urllib.request.Request(url, headers=hdr, data = bytes(data.encode("utf-8")))
        req.get_method = lambda: 'POST'
        response = urllib.request.urlopen(req)
        df = pd.read_json(response)

        df.to_json('taxon_list.json', index=False)

    except Exception as e:
        print(e)

get_observations()