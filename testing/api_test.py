from database.seed import seed_Db
from database.api import API

# observations_export('testing/medium_dataset')
#API.auth_token()
seed_Db.obs_query_loop()

# input("")