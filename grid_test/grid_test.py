import json
import os

import pandas as pd
import requests

from database.db import FenologikDb

def get_country_polygon():
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "country": "Sweden",
        "format": "json",
        "polygon_geojson": 1
    }
    headers = {
        "User-Agent": "Fenologik (olsson.christoffer@pm.me)" # FIX: Add to environment variables
    }

    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        data = json.loads(response.text)
        if data:
            return data[0]["geojson"]            
        else:
            return None
    else:
        print(f"Request failed with status code {response.status_code}")
        return None
    
def convert_geojson_to_postgis(polygon_geojson):
    # Convert the GeoJSON polygon to a string
    polygon_geojson_str = json.dumps(polygon_geojson)

    # Connect to PostgreSQL database
    db = FenologikDb(os.environ["DATABASE_URL"])
    session = db.get_session()
    conn = session.connection().connection
    cur = conn.cursor()

    # Use ST_GeomFromGeoJSON to convert the GeoJSON polygon to a PostGIS geometry
    cur.execute(f"""
        CREATE TABLE polygon AS
        SELECT ST_GeomFromGeoJSON('{polygon_geojson_str}') AS geom;
    """)

    #postgis_geom = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

# polygon_geojson = get_country_polygon()
# postgis_geom = convert_geojson_to_postgis(polygon_geojson)
# print(type(postgis_geom))

# Creates a square grid with 11 different zoom levels
# When testing, remove zoom level first, then id if errors occur
def create_grid():
    db = FenologikDb(os.environ["DATABASE_URL"])
    session = db.get_session()
    conn = session.connection().connection
    cur = conn.cursor()   

    sizes = [51200, 25600, 12800, 6400, 3200, 1600, 800, 400, 200, 100, 50]
    for zoom_level, size in enumerate(sizes):
        cur.execute(f"""
            WITH create_grid AS (
            SELECT (ST_SquareGrid({size}, geom_3857)).*,
                   {zoom_level} AS zoom_level
            FROM polygon WHERE name = 'Sweden'
            ),

            insertion AS (
            SELECT create_grid.geom AS geom,
                   create_grid.zoom_level AS zoom_level
            FROM create_grid, polygon
            WHERE ST_Intersects(create_grid.geom, polygon.geom_3857)
            )

            INSERT INTO square_grid (id, geom, zoom_level)
            SELECT DEFAULT, geom, zoom_level
            FROM insertion;
        """)

# Counts the number of observations per tile, taxon and date
# Untested
def count_obs_per_tile():
    db = FenologikDb(os.environ["DATABASE_URL"])
    session = db.get_session()
    conn = session.connection().connection
    cur = conn.cursor()   

    cur.execute("""
        SELECT COUNT(*) AS obs_count, tile_id, taxon_id, obs_date
        FROM tile_obs_count
        GROUP BY tile_id, taxon_id, obs_date;
    """)

    obs_per_tile = cur.fetchall()
    obs_per_tile_df = pd.DataFrame(obs_per_tile, columns=["obs_count", "tile_id", "taxon_id", "obs_date"])
    obs_per_tile_df.to_csv("obs_per_tile.csv", index=False)
    print(obs_per_tile_df)

# convert_geojson_to_postgis(get_country_polygon())
# create_grid()