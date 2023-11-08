import requests
from database.models import Tile
from xml.etree import ElementTree as ET
import base64
import os
import time
from sqlalchemy import and_, desc
import traceback

MAX_Z_LEVEL = 10 #The further up this number is, up to 14, the more detailed and tinier scales are allowed on the map.
TOKEN_LIFETIME = 3550 #Tokens lifetime in seconds, in order to automatically refresh it.

class MapAPI():

    #Gets last tile found in the database, in order to continue where it left off in case of crashes or unexpected behaviour.
    @staticmethod
    def get_last_tile(session):
        last_tile = session.query(Tile).order_by(
            desc(Tile.z), desc(Tile.y), desc(Tile.x)
        ).first()
        return last_tile
    
    #Generates access token to be used when fetching tiles.
    @staticmethod
    def get_access_token(consumer_key,consumer_secret):
        url = 'https://apimanager.lantmateriet.se/oauth2/token'


        credentials = f"{consumer_key}:{consumer_secret}"
        credentials_encoded = base64.b64encode(credentials.encode()).decode()

        hdr = {
            "Authorization": f"Basic {credentials_encoded}"
        }

        data = {
            "grant_type":"client_credentials"
        }

        response = requests.post(url, headers=hdr, data=data, verify=False)

        if response.status_code == 200:
            access_token = response.json().get('access_token')
            return access_token
        else:
            print(f"Failed to get access token. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    
    #The three methods below controls token creation in order to call the API, made to always have an access token when fetching tiles.
    #refresh_token_if_expired() is called in the giant loop that fetches the data and inputs it into our database.

    def is_token_expired(self):
        return (time.time() - self.token_creation_time) >= TOKEN_LIFETIME

    def refresh_token_if_expired(self):
        if self.is_token_expired():
            self.access_token = self.generate_new_token()
            self.token_creation_time = time.time()

    def generate_new_token(self):
        return self.get_access_token(os.environ['CONSUMER_KEY'], os.environ['CONSUMER_SECRET'])

    def __init__(self, db):
        self.token_creation_time = time.time()
        self.access_token = self.generate_new_token()
        self.db = db


    def fetch_tile(self, z, y, x):
            url = f'https://api.lantmateriet.se/open/topowebb-ccby/v1/wmts/token/{self.access_token}/1.0.0/topowebb/default/3857/{z}/{y}/{x}.png'
            response = requests.get(url)
            print(url)
            time.sleep(0.011)

            if response.status_code == 200:
                return Tile(z=z, y=y, x=x, tile_data=response.content)
            else:
                print(f'Failed to fetch tile {z},{y},{x}. Status code: {response.status_code}')
                return None

    def fetch_and_store_tiles(self, bulk_size=100):
        session = self.db.get_session()
        capabilities_url = f'https://api.lantmateriet.se/open/topowebb-ccby/v1/wmts/token/{self.access_token}/?request=GetCapabilities&version=1.0.0&service=wmts'
        response = requests.get(capabilities_url)
        root = ET.fromstring(response.content)
        tiles_to_add = []
        
        contents = root.find('{http://www.opengis.net/wmts/1.0}Contents')

        # Iterate through TileMatrixSet elements
        for tile_matrix_set in contents.iter('{http://www.opengis.net/wmts/1.0}TileMatrixSet'):
            identifier_element = tile_matrix_set.find('{http://www.opengis.net/ows/1.1}Identifier')

            if identifier_element is not None:
                identifier = identifier_element.text
                print(f'Identifier:{identifier}')

                if identifier == '3857':
                    empty_tile_count = 0
                    max_empty_tiles = 25
                    for tile_matrix in tile_matrix_set.iter('{http://www.opengis.net/wmts/1.0}TileMatrix'):
                        try:
                            matrix_id = int(tile_matrix.find('{http://www.opengis.net/ows/1.1}Identifier').text)
                            matrix_width = int(tile_matrix.find('{http://www.opengis.net/wmts/1.0}MatrixWidth').text)
                            matrix_height = int(tile_matrix.find('{http://www.opengis.net/wmts/1.0}MatrixHeight').text)
                            
                            last_tile = self.get_last_tile(session)

                            # if (matrix_id > last_tile.z) or \
                            #    (matrix_id == last_tile.z and row > last_tile.y) or \
                            #    (matrix_id == last_tile.z and row == last_tile.y and col > last_tile.x):

                            for row in range(matrix_height):
                                for col in range(matrix_width):
                                    tile = self.fetch_tile(matrix_id, row, col)
                                    if tile:
                                        existing_tile = session.query(Tile).filter(
                                            and_(
                                                Tile.z == tile.z,
                                                Tile.y == tile.y,
                                                Tile.x == tile.x
                                            )
                                        ).first()

                                        if existing_tile is None:
                                            tiles_to_add.append(tile)
                                    else:
                                        empty_tile_count += 1
                                        if empty_tile_count >= max_empty_tiles:
                                            break
                                    if len(tiles_to_add) >= bulk_size:
                                        session.bulk_save_objects(tiles_to_add)
                                        session.commit()
                                        tiles_to_add = []
                                if empty_tile_count >= max_empty_tiles:
                                    break
                        except Exception as e:
                            print(f'An error occurred: {e}')
                            traceback.print_exc()

            # Commit any remaining tiles
            if tiles_to_add:
                session.bulk_save_objects(tiles_to_add)
                session.commit()

