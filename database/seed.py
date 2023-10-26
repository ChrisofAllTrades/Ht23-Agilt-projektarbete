from datetime import datetime
import json
import os

from dateutil.relativedelta import relativedelta
import pandas as pd
from urllib import request

from database.api import API

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
            endDateStr = endDate.strftime("%Y%m%d")
            startDateStr = startDate.strftime("%Y%m%d")

            url = ("https://api.artdatabanken.se/species-observation-system/v1/Exports/Order/GeoJson"
                f"?descripion={startDateStr}-{endDateStr}"
                "&validateSearchFilter=true"
                "&sensitiveObservations=false"
                "&sendMailFromZendTo=true"
                "&cultureCode=sv-SE"
            )
            
            # Request header
            hdr = API.hdr
            hdr["Authorization"] = os.environ["AUTH_TOKEN"]

            # Request body
            body = {
                "output": {
                    "fields": [
                        "occurrence.occurrenceId",
                        "taxon.id",
                        "event.startDate",
                        "event.endDate",
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
                
                # Request query to download observations as GeoJSON
                req = request.Request(url, headers=API.hdr, data=bytes(json.dumps(body).encode("utf-8")))
                req.get_method = lambda: "POST"

                # Opens the request url and reads the response
                with request.urlopen(req) as response:
                    data = response.read()
                    status_message = data.decode("utf-8")
                    
                    # Adds status id to dictionary and prints the id of the last request
                    request_status_dict[startDate.strftime("%Y%m%d") + "-" + endDate.strftime("%Y%m%d")] = status_message
                    last_key = list(request_status_dict.keys())[-1]
                    last_value = request_status_dict[last_key]
                    print(f"Status id for request {last_key}: {last_value}")

                # Pauses loop after first iteration to allow for manual inspection of data before continuing
                if first_iteration:
                    input("Check received data before continuing")
                    startDate = endDate - relativedelta(months=6)
                    first_iteration = False

            # If observation count exceeds 2 000 000, narrow search
            elif obs_count > 2000000:
                print("\033[1;31mToo many observations, narrowing search\033[0m")
                startDate = startDate + relativedelta(months=1)
            
            print("Export orders made: " + str(export_orders_count) + ". Now filtering between", startDateStr, "and", endDateStr)  

    # Retrieve taxon list from SOS API
    def taxon_list():
        url = "https://api.artdatabanken.se/taxonlistservice/v1/taxa"

        body = {
            "conservationListIds": [245],
            "outputFields": ["id", "scientificname", "swedishname", "englishname"]
            }

        req = request.Request(url, headers=API.hdr, data = bytes(json.dumps(body).encode("utf-8")))
        req.get_method = lambda: "POST"

        response = request.urlopen(req)
        df = pd.read_json(response)

        df.to_csv("taxon_list.csv", index=False)