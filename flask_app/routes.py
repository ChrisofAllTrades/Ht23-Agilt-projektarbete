from . import app
from database.models import Tile
from database.db import fenologikDb
from streamlit_functions.map_api_test import MapAPI
import io
from flask import send_file, make_response, jsonify
from sqlalchemy import and_
import os

#As the flask server is the only thing that needs to have a connection with the db, it's initialized here. (As all requests go through routes)

#########################################
#  - Database and MapAPI connections -  #
#########################################


db = fenologikDb(os.environ['DATABASE_URL'])
db.setup()
map_api = MapAPI(db)


###########################################################
#  - Routes to be called in other parts of the program -  #
###########################################################

#Note: Add more routes for fetching individual data points, graphics, etc.
#Note: Can be changed to be populating databases through Routes with secured access.

@app.route('/')
def root():
    return "Flask app is running!"

@app.route('/get_tile/<int:z>/<int:x>/<int:y>')
def get_tile(z, x, y):
    session = db.get_session()
    tile = session.query(Tile).filter(
            and_(
                Tile.z == z,
                Tile.x == x,
                Tile.y == y
                )
            ).first()
    
    if tile:
        # Create a file-like object from the tile data
        tile_bytes = io.BytesIO(tile.tile_data)
        
        # Create and return the response
        response = make_response(send_file(tile_bytes, mimetype='image/png'))
        return response
    else:
        # Handle the case where the tile is not found in the database
        return "Tile not found", 404
    
@app.route('/populate_tiles_table') #Unsafe as of yet, anyone can access it.
def populate_tiles_table():
    try:
        map_api.fetch_and_store_tiles()
        return jsonify({"message": "Tiles downloaded and merged into database successfully!"}), 200
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": str(e)}), 500