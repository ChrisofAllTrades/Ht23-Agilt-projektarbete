import urllib.request, json
import pandas as pd
# import streamlit as st
import os

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
            "ids": [100090],
        }
    }
    data = json.dumps(data)
    req = urllib.request.Request(url, headers=hdr, data = bytes(data.encode("utf-8")))

    req.get_method = lambda: 'POST'
    
    # Send HTTP request and load response into pandas dataframe
    response = urllib.request.urlopen(req)
    df = pd.read_json(response)

    # Save pandas dataframe to csv
    df.to_csv('data.csv', index=False)
except Exception as e:
    print(e)