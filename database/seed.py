from datetime import datetime
import json
import os
import random

from dateutil.relativedelta import relativedelta
import pandas as pd
from urllib import request

from database.api import API

class Seed_Db:
    def __init__():
        pass



    # SOS API query loop for collecting entire observations dataset
    # 2 000 000 observations max per call.
    def obs_query_loop():
        # endDate = datetime.today().date()
        endDate = datetime(2021, 1, 31).date()
        startDate = endDate - relativedelta(months=6)

        obs_count = 1
        total_count = 0
        first_iteration = True
        export_orders_count = 0
        request_status_dict = {}
        
        # Loop through API dataset until all observations have been collected
        while obs_count > 0:
            endDateDsc = endDate.strftime("%Y%m%d")
            startDateDsc = startDate.strftime("%Y%m%d")
            
            endDateStr = endDate.strftime("%Y-%m-%d")
            startDateStr = startDate.strftime("%Y-%m-%d")

            # Description doesn't seem to work so it's commented out for now
            url = ("https://api.artdatabanken.se/species-observation-system/v1/Exports/Order/GeoJson"
                f"?descripion={startDateDsc}-{endDateDsc}"
                "&validateSearchFilter=true"
                "&sensitiveObservations=false"
                "&sendMailFromZendTo=true"
                "&cultureCode=sv-SE"
            )
            
            # Request header
            API.hdr["Authorization"] = os.environ["AUTH_TOKEN"]

            # Request body
            body = API.body.copy() 
            body["date"] = {
                    "startDate": startDateStr,
                    "endDate": endDateStr
                }
                
            obs_count = API.obs_count(body)

            # Adjust date range of query depending on average number of observations per day in time range
            def date_range_adjustment(obs_count, endDate, startDate):
                obs_target = 2000000

                # Observations per day in time range
                obs_average = obs_count / (endDate - startDate).days
                # Multiply by difference between target and current observation count
                adjustment = ((obs_target - obs_count) / obs_average) - random.randint(5, 20)
                # Adjust time range
                startDate = startDate - relativedelta(days=adjustment)

                return startDate

            # Sequence of if statements to determine next query date range
            if obs_count == 0:
                print("Observation count is 0. Stopping.")
                print("The status ids of the export orders are:", request_status_dict)
                break
            
            # If obs count is less than 1 800 000, increase date range
            elif obs_count < 1800000 and startDate.year >= 1600:
                startDate = date_range_adjustment(obs_count, endDate, startDate)
                print(f"\033[93mToo few observations, widening search to between {startDate} and {endDate}\033[0m")
            
            elif obs_count < 2000000 and obs_count > 1800000 or startDate.year < 1600:
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

                # Increments export orders count
                export_orders_count += 1
                total_count = total_count + obs_count

                # Adjusts date range for next query
                endDate = startDate - relativedelta(days=1)
                startDate = endDate - relativedelta(months=6)

                print("Export orders made: " + str(export_orders_count) + " (" + str(total_count) + " total observations). Now filtering between", startDate, "and", endDate)
                
                # Pauses loop after first and fifth iteration to allow for manual inspection of data before continuing
                if first_iteration:
                    input("Check received data before continuing")
                    first_iteration = False
                elif export_orders_count % 6 == 0:
                    input("Six simultaneous requests made, which is the API limit. Await response before continuing")

            # If obs count is more than 2 000 000, decrease date range
            elif obs_count > 2000000:
                startDate = date_range_adjustment(obs_count, endDate, startDate)
                print(f"\033[91mToo many observations, narrowing search to between {startDate} and {endDate}\033[0m")
        


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

        df.to_csv("taxon_list_test.csv", index=False)