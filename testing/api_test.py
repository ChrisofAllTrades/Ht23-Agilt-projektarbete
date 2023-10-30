from database.seed import seed_Db
from database.api import API

# observations_export('testing/medium_dataset')
#API.auth_token()
seed_Db.obs_query_loop()
# API.transform_observations(API.get_observations(), "test.csv")
#API.obs_export_download("medium_test.csv")

# input("")