from database.api import API
from database.db import FenologikDb
from database.models import Observations, Taxa
from database.seed import Seed_Db

#Observations.models()

Seed_Db.obs_query_loop()

#FenologikDb.extract_id("testing/observations_Id_Test.geojson")
#FenologikDb.transform_data("testing/full_dataset/1/Observations.geojson")
#FenologikDb.populate_database("testing/full_dataset/1/Observations.geojson")

#API.auth_token()
#API.get_observations()
#API.obs_export_download("id_Testing")
#API.dataProvider_obs_count()

# input("")