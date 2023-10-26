from database.api import API
from database.db import fenologikDb
from database.seed import seed_Db

# observations_export('testing/medium_dataset')
#seed_Db.obs_query_loop()

#API.auth_token()
API.get_observations()
#API.obs_export_download("medium_test")
#API.dataProvider_obs_count()

#fenologikDb.extract_id("testing/full_dataset/2/Observations.geojson")

# input("")