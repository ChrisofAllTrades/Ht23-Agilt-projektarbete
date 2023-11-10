import json
import os

import geopandas as gpd
import pandas as pd
import requests
from sqlalchemy import text

from database.db import FenologikDb

class ObservationGrid:

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
            INSERT INTO polygon (geom, name, geom_3857)        
            SELECT ST_GeomFromGeoJSON('{polygon_geojson_str}') AS geom,
                'Sweden' AS name,
                ST_Transform(ST_GeomFromGeoJSON('{polygon_geojson_str}'), 3857) AS geom_3857
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

        # sizes = [51200, 25600, 12800, 6400, 3200, 1600, 800, 400, 200, 100, 50]
        sizes = [25600]
        for zoom_level, size in enumerate(sizes):
            cur.execute(f"""
                WITH create_grid AS (
                SELECT (ST_SquareGrid({size}, geom_3857)).*,
                    1 AS zoom_level
                FROM polygon WHERE name = 'Sweden'
                ),

                insertion AS (
                SELECT create_grid.geom AS geom,
                    create_grid.zoom_level AS zoom_level
                FROM create_grid, polygon
                WHERE ST_Intersects(create_grid.geom, polygon.geom_3857)
                )

                INSERT INTO square_grid (geom, zoom_level)
                SELECT geom, zoom_level
                FROM insertion;
            """)

        # cur.execute(f"""
        #     WITH create_grid AS (
        #     SELECT (ST_SquareGrid(51200, geom_3857)).*
        #     FROM polygon WHERE name = 'Sweden'
        #     ),

        #     insertion AS (
        #     SELECT create_grid.geom AS geom
        #     FROM create_grid, polygon
        #     WHERE ST_Intersects(create_grid.geom, polygon.geom_3857)
        #     )

        #     INSERT INTO square_grid (geom)
        #     SELECT geom
        #     FROM insertion;
        # """)

        conn.commit()
        cur.close()
        conn.close()

    # Counts the number of observations per tile, taxon and date
    # Untested
    def count_obs_per_tile():
        db = FenologikDb(os.environ["DATABASE_URL"])
        session = db.get_session()
        conn = session.connection().connection
        cur = conn.cursor()

        # Define the SQL query
        query = text("""
            INSERT INTO tile_obs_count (tile_id, taxon_id, obs_date, obs_count)
            SELECT
                square_grid.id AS tile_id,
                taxa.id AS taxon_id,
                DATE(observations.start_date) AS obs_date,
                SUM(observations.organism_quantity) AS obs_count
            FROM
                square_grid
                JOIN observations ON ST_Intersects(square_grid.geom, ST_Transform(observations.position, 3857))
                JOIN taxa ON observations.taxon_id = taxa.id
            WHERE square_grid.zoom_level = 1
            GROUP BY
                square_grid.id,
                DATE(observations.start_date),
                taxa.id
        """)

        # Execute the SQL query
        cur.execute(str(query))

        # Commit the changes and close the connection
        conn.commit()
        cur.close()
        conn.close()

    def grid_visualization():
        db = FenologikDb(os.environ["DATABASE_URL"])
        session = db.get_session()

        query = """
            SELECT square_grid.geom, tile_obs_count.obs_count
            FROM square_grid
            JOIN tile_obs_count ON square_grid.id = tile_obs_count.tile_id
        """

        gdf = gpd.GeoDataFrame.from_postgis(query, session.connection(), geom_col="geom")

        geojson = gdf.to_json()

        # Set the display options
        # pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', None)

        # print(geojson)
        return geojson

# convert_geojson_to_postgis(get_country_polygon())
# create_grid()
# count_obs_per_tile()
# grid_visualization()