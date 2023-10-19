import pandas as pd
import json
from sqlalchemy import create_engine # MetaData, Table, Column, Integer, String
import os

# What is the name of the json file?
data_file = 'taxon_list.json'
# What column contains the data dictionary?
data_column = 'natureConservationListTaxa'
# What dictionary key contains the data?
data_key = 'taxonInformation'
# What is the name of the table in the database?
seed_table_name = 'taxa'


# Exctract data from json file and return as pandas dataframe with normalized data
df = pd.read_json(data_file)
df[data_column] = df[data_column].apply(lambda x: json.loads(json.dumps(x)))
df = pd.json_normalize(df[data_column], data_key)
engine = create_engine(os.environ['DATABASE_URL'])

# Send the DataFrame to database
# Can't update existing table with overlapping data so we replace it instead, needs to be changed
df.to_sql(seed_table_name, engine, if_exists='replace', index=False)

print('Done!')