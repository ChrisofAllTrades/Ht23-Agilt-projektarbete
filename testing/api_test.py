from database.api import API
from database.db import FenologikDb
from database.models import Observations, Taxa
from database.seed import Seed_Db

#Observations.models()

#Seed_Db.obs_query_loop()

#FenologikDb.extract_id("testing/observations_Id_Test.geojson")
#FenologikDb.transform_observations(FenologikDb, "id_Testing.geojson/Observations.geojson")
#FenologikDb.transform_taxa("testing/taxon_list.json")
FenologikDb.populate_taxa(FenologikDb, "taxa.json")
FenologikDb.populate_observations(FenologikDb, "medium_observations/Observations.geojson")

#API.auth_token()
#API.get_observations()
#API.obs_export_download("medium_observations")
#API.dataProvider_obs_count()
#API.get_taxa()

# input("")
