import pandas as pd
import json
import urllib.request
import zipfile
import io
import os
# from sqlalchemy import create_engine # MetaData, Table, Column, Integer, String
# from sqlalchemy.orm import sessionmaker
from dateutil.relativedelta import relativedelta
from datetime import datetime
from database.api import API

# Change to DwC-A or keep CSV format?
#   I don't see the need for it right now
# To do: Add function for Exports_OrderCsv (2 000 000 observations max per call)
#   - Observations need timestamp.

class seed_Db:

    def __init__():
        pass

    # SOS API query loop for collecting entire observations dataset
    # 2 000 000 observations max per call.
    def obs_query_loop():
        endDate = datetime.today().date()
        startDate = endDate - relativedelta(days=1)
        
        # endDate = datetime(2023, 10, 24)
        # startDate = datetime(2023, 10, 14)

        obs_count = 1
        first_iteration = True
        export_orders_count = 0
        request_status_dict = {}
        
        # Loop through API dataset until all observations have been collected
        while obs_count > 0:
            endDateStr = endDate.strftime('%Y%m%d')
            startDateStr = startDate.strftime('%Y%m%d')

            url = ("https://api.artdatabanken.se/species-observation-system/v1/Exports/Order/Csv"
                f"?descripion={startDateStr}-{endDateStr}"
                "&validateSearchFilter=true"
                "&propertyLabelType=PropertyPath"
                "&sensitiveObservations=false"
                "&sendMailFromZendTo=true"
                "&cultureCode=sv-SE"
            )
            
            # Request body
            body = {
                "output": {
                    "fields": [
                        "occurrence.occurrenceId",
                        "taxon.id",
                        "event.startDate",
                        "event.endDate",
                        "event.plainStartTime",
                        "event.plainEndTime",
                        "location.Sweref99TmX",
                        "location.Sweref99TmY"
                    ]
                },
                "date": {
                    "startDate": startDate.strftime('%Y-%m-%d'),
                    "endDate": endDate.strftime('%Y-%m-%d'),
                },
                "taxon": {
                    "includeUnderlyingTaxa": True,
                    "ids": [4000104]
                }
            }

            obs_count = API.obs_count(body)

            # Sequence of if statements to determine next query date range
            if obs_count == 0:
                print("Observation count is 0. Stopping.")
                print("The status ids of the export orders are:", request_status_dict)
                break
            elif obs_count < 2000000:
                endDate = startDate - relativedelta(days=1)
                export_orders_count += 1
                if startDate.year >= 2004:
                    startDate = endDate - relativedelta(months=6)
                elif startDate.year >= 2000:
                    startDate = endDate - relativedelta(years=2)
                elif startDate.year >= 1990:
                    startDate = endDate - relativedelta(years=3)
                elif startDate.year >= 1980:
                    startDate = endDate - relativedelta(years=8)
                else: 
                    startDate = endDate - relativedelta(years=400)
                
                # Request query to download observations as CSV
                req = urllib.request.Request(url, headers=API.hdr, data=bytes(json.dumps(body).encode("utf-8")))
                req.get_method = lambda: "POST"

                with urllib.request.urlopen(req) as response:
                    data = response.read()
                    status_message = data.decode("utf-8")
                    request_status_dict[startDate.strftime("%Y%m%d") + "-" + endDate.strftime("%Y%m%d")] = status_message
                    print(status_message)

                if first_iteration:
                    input("Check received data before continuing")
                    startDate = endDate - relativedelta(months=6)
                    first_iteration = False

            # If observation count exceeds 2 000 000, narrow search
            elif obs_count > 2000000:
                print('\033[1;31mToo many observations, narrowing search\033[0m')
                startDate = startDate + relativedelta(months=1)
            
            print("Export orders made: " + str(export_orders_count) + ". Now filtering between", startDate.strftime("%Y-%m-%d"), "and", endDate.strftime("%Y-%m-%d"))  

    # Retrieve taxon list from SOS API
    def taxon_list():
        url = "https://api.artdatabanken.se/taxonlistservice/v1/taxa"

        body = {
            "conservationListIds": [245],
            "outputFields": ["id", "scientificname", "swedishname", "englishname"]
            }

        req = urllib.request.Request(url, headers=API.hdr, data = bytes(json.dumps(body).encode("utf-8")))
        req.get_method = lambda: 'POST'

        response = urllib.request.urlopen(req)
        df = pd.read_json(response)

        df.to_csv('taxon_list.csv', index=False)