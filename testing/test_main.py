from database.db import fenologikDb
import database.api as api
import os

db = fenologikDb(os.environ['DATABASE_URL'])
# db.setup()
# api.transform_observations()
api.populate_database()