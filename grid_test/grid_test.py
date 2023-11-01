import psycopg2
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon
import numpy as np

# Step 1: Connect to the PostgreSQL database and fetch the data
conn = psycopg2.connect(database="fenologik", user="focus", password="Babaganoush1.", host="localhost", port="5432")
cur = conn.cursor()
cur.execute("SELECT latitude, longitude FROM observations")
rows = cur.fetchall()

# Step 2: Convert the data into a GeoDataFrame
geometry = [Point(xy) for xy in rows]
gdf = gpd.GeoDataFrame(geometry=geometry)

# Step 3: Create a grid of tiles over the area of interest
xmin, ymin, xmax, ymax = gdf.total_bounds
width = height = 0.1  # width and height of a grid tile
rows = int(np.ceil((ymax-ymin) /  height))
cols = int(np.ceil((xmax-xmin) / width))
XleftOrigin = xmin
XrightOrigin = xmin + width
YtopOrigin = ymax
YbottomOrigin = ymax- height
polygons = []
for i in range(cols):
    Ytop = YtopOrigin
    Ybottom =YbottomOrigin
    for j in range(rows):
        polygons.append(Polygon([(XleftOrigin, Ytop), (XrightOrigin, Ytop), (XrightOrigin, Ybottom), (XleftOrigin, Ybottom)]))
        Ytop = Ytop - height
        Ybottom = Ybottom - height
    XleftOrigin = XleftOrigin + width
    XrightOrigin = XrightOrigin + width
grid = gpd.GeoDataFrame({'geometry':polygons})

# Step 4: Count the number of observations in each tile
count = gpd.sjoin(gdf, grid, how='right', op='within').groupby('index_right').size()
grid['count'] = count.values

# Step 5: Visualize the grid with a color map representing the count of observations
fig, ax = plt.subplots()
grid.plot(column='count', cmap='viridis', linewidth=0.8, ax=ax, edgecolor='0.8', legend=True)
plt.show()