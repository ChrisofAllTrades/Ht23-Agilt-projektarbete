from database.api import API
from database.db import FenologikDb
from grid_test.grid_test import ObservationGrid
import os

######################
### Database setup ###
######################

# Connect to database
db = FenologikDb(os.environ['DATABASE_URL'])

# # Create tables
db.setup()
input("Tables created. Press enter to continue.")

# Populate taxa and observations tables (the latter with test data from a single day)
FenologikDb.populate_taxa(FenologikDb, "taxa.json")
FenologikDb.populate_observations(FenologikDb, "medium_observations/Observations.geojson")
input("Database population complete. Press enter to continue.")

# Get polygon of Sweden's borders from OpenStreetMap and add it to the polygon table
ObservationGrid.convert_geojson_to_postgis(ObservationGrid.get_country_polygon())
input("Polygon with border of Sweden stored in polygon table. Press enter to continue.")

# Create a test square grid with two zoom levels and add it to the square_grid table
ObservationGrid.create_grid()
input("Square grid created. Press enter to continue.")

# Count observations per tile and add them to the tile_obs_count table
# Currently makes the count on zoom_level 1, which is the smallest grid. Later on the higher zoom levels will use the counts from the lower ones
ObservationGrid.count_obs_per_tile()
input("Job done! Continue with the next step in README.md")