from database.api import API
from database.db import FenologikDb
import os

######################
### Database setup ###
######################

# Connect to database
db = FenologikDb(os.environ['DATABASE_URL'])

# # Create tables
db.setup()

# Change id column to auto-increment (doesn't work, requires altering table manually)
# db.table_id_sequence()

input("Pause for manual database setup. Refer to item 5. in Database Setup in README.md. When done, press enter to continue.")

# Populate tables with test data in testing/observations.csv
API.populate_database()
