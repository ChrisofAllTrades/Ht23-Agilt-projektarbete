import streamlit as st
import psycopg2
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon
import numpy as np
import os

def main():
    st.title("Fenologik")
    # Step 1: Connect to the PostgreSQL database and fetch the data
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cur = conn.cursor()

    cur.execute("SELECT latitude, longitude FROM observations WHERE taxon_id = 100006")

    # Step 2: Convert the data into a GeoDataFrame
    geometry = [Point(xy) for xy in rows]
    gdf = gpd.GeoDataFrame(geometry=geometry)

    # Step 3: Create a grid of tiles over the area of interest
    cur.execute("SELECT MIN(latitude), MIN(longitude), MAX(latitude), MAX(longitude) FROM observations")
    xmin, ymin, xmax, ymax = cur.fetchone()

    width = height = 0.1  # width and height of a grid tile
    rows = int(np.ceil((ymax-ymin) /  height))
    cols = int(np.ceil((xmax-xmin) / width))
    XleftOrigin = xmin
    XrightOrigin = xmin + width
    YtopOrigin = ymax
    YbottomOrigin = ymax - height
    polygons = []
    for i in range(cols):
        Ytop = YtopOrigin
        Ybottom = YbottomOrigin
        for j in range(rows):
            polygons.append(Polygon([(XleftOrigin, Ytop), (XrightOrigin, Ytop), (XrightOrigin, Ybottom), (XleftOrigin, Ybottom)]))
            Ytop = Ytop - height
            Ybottom = Ybottom - height
        XleftOrigin = XleftOrigin + width
        XrightOrigin = XrightOrigin + width
    grid = gpd.GeoDataFrame({'geometry':polygons}, crs="EPSG:4326")

    # # Calculate the centroid of each polygon
    # grid['centroid'] = grid['geometry'].centroid

    # # Sort the grid by the x and y coordinates of the centroid
    # grid['x'] = grid['centroid'].x
    # grid['y'] = grid['centroid'].y
    # grid = grid.sort_values(by=['y', 'x'])

    # # Drop the centroid column as it's no longer needed
    # grid = grid.drop(columns='centroid')

    grid = grid.to_crs(epsg=4326)

    # Continue with the rest of your code
    count = gpd.sjoin(gdf, grid, how='right', op='within').groupby('index_left').size()
    grid['count'] = grid.index.map(count).fillna(0)

    fig, ax = plt.subplots()
    grid.plot(column='count', cmap='viridis', linewidth=0.8, ax=ax, edgecolor='0.8', legend=True)
    st.pyplot(fig)

if __name__ == "__main__":
    main()