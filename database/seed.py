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
#     I don't see the need for it right now
# To do: Add function for Exports_OrderCsv (2 000 000 observations max per call)
# To do: Observations need timestamp. Include in date column or add new column?
# To do: Rebuild function for querying API for taxa
# To do: Clean up existing functions

class seed_Db:

    def __init__():
        pass

    # SOS API query loop for collecting entire observations dataset
    # 2 000 000 observations max per call.
    def obs_query_loop():
        endDate = datetime.today().date()
        startDate = endDate - relativedelta(months=6)
        endDateStr = endDate.strftime('%Y%m%d')
        startDateStr = startDate.strftime('%Y%m%d')

        url = ("https://api.artdatabanken.se/species-observation-system/v1/Exports/Order/Csv"
               f"?descripion={startDateStr}-{endDateStr}"
               "&outputFieldSet=Minimum"
               "&validateSearchFilter=true"
               "&propertyLabelType=PropertyPath"
               "&sensitiveObservations=false"
               "&sendMailFromZendTo=true"
               "&cultureCode=sv-SE")
        

        # endDate = datetime(1950, 1, 1)
        # startDate = datetime(1985, 1, 1)

        obs_count = 1
        first_iteration = True
        export_orders_count = 0
        request_status_dict = {}
        
        # Loop through API dataset until all observations have been collected
        while obs_count > 0:
            # Request body
            body = {
                "output": {
                    "fields": [
                        "Occurrence.OccurrenceId",
                        "Taxon.Id",
                        "Event.StartDate",
                        "Event.EndDate",
                        "location.Sweref99TmX",
                        "location.Sweref99TmY"
                    ]
                },
                "date": {
                    "startDate": startDateStr,
                    "endDate": endDateStr,
                    "dateFilterType": "OverlappingStartDateAndEndDate"
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

    # Uses Exports_DownloadCsv operation of the SOS API to download observations as CSV
    # 25 000 observations max per call, throws error 400 if exceeded
    # CHANGE: Move to api.py
    # def obs_export_download(self, csv_save_path):
    #     try:
    #         url = 'https://api.artdatabanken.se/species-observation-system/v1/Exports/Download/Csv?outputFieldSet=Minimum&validateSearchFilter=true&propertyLabelType=PropertyPath&cultureCode=sv-SE&gzip=true&sensitiveObservations=false'

    #         # Request body
    #         body = {
    #             "Output": {
    #                 "Fields": [
    #                     "Occurrence.OccurrenceId",
    #                     "Taxon.Id",
    #                     "Event.StartDate",
    #                     "Event.EndDate",
    #                     "location.Sweref99TmX",
    #                     "location.Sweref99TmY"
    #                 ]
    #             },
    #             "date": {
    #                 "startDate": "2023-01-01",
    #                 "endDate": "2023-01-31",
    #                 "dateFilterType": "OverlappingStartDateAndEndDate"
    #             },
    #             "taxa": {
    #                 "ids": [4000104],
    #                 "includeUnderlyingTaxa": True
    #             }
    #         }
    #         # save_path = '/testing/medium_observations.csv'
    #         req = urllib.request.Request(url, headers=seed_db.hdr, data=bytes(json.dumps(body).encode("utf-8")))
    #         req.get_method = lambda: 'POST'

    #         with urllib.request.urlopen(req) as response:
    #             data = response.read()

    #         with zipfile.ZipFile(io.BytesIO(data)) as z:
    #             z.extractall(csv_save_path)
    #         # data = json.dumps(data)
    #         # req = urllib.request.Request(url, headers=hdr, data = bytes(data.encode("utf-8")))
    #         # req.get_method = lambda: 'POST'

    #         # # Send HTTP request and load response into pandas dataframe
    #         # response = urllib.request.urlopen(req)
    #         # return response
    #     except Exception as e:
    #         print(e)

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