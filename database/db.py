import json
import os

from geoalchemy2 import Geometry, WKTElement
import geopandas as gpd
import pandas as pd
from shapely import wkt # FIX: Remove if not used
from shapely.wkb import loads
from shapely.geometry import mapping
from sqlalchemy import create_engine, text
from sqlalchemy.orm import load_only, sessionmaker # FIX: Remove if not used

from database.models import Base, Observations, Taxa, Polygon, Square_Grid, Tile_Obs_Count

# To do: Add method for processing entire dataset in chunks
# To do: Clean up class to separate database functions from query functions


##########################################
### Database class and query functions ###
##########################################


class FenologikDb:
    def __init__(self, database_uri):
        self.engine = create_engine(database_uri, echo=True)
        self.Session = sessionmaker(bind=self.engine)

    def get_session(self):
        return self.Session()

    # def query(self, model):
    #     session = self.get_session()
    #     result = session.query(model).all()
    #     session.close()
    #     return result
    
    def setup(self):
        Base.metadata.create_all(self.engine)


####################################
### Methods for data preparation ###
####################################


    # Creates a primary key id for observations table from id column in GeoJson file
    def generate_pk(data):
        gdf = gpd.read_file(data)

        # Mapping between URN prefix and id corresponding to data provider id plus a leading 0 if < 10, e.g. 01 for Artportalen)
        urn_mapping = {
            "urn:lsid:artportalen.se:sighting:": "01",
            "NRM:RingedBirds:": "09",
            "biologg-": "18",
            "https://www.inaturalist.org/observations/": "19",
            "SFTkfr:": "20",
            "SFTspkt:": "21",
            "SFTstd:": "22",
            "KBV:occurrenceID:": "23"
        }

        # Extract the id column from the GeoDataFrame
        occurrence_id = gdf["id"]

        # Split the OccurrenceId column into two columns, one with the URN prefix and one with the id
        def split_id(occurrence_id):
            if occurrence_id.startswith("biologg-"):
                index = occurrence_id.rfind("-")
            elif occurrence_id.startswith("https://www.inaturalist.org/observations/"):
                index = occurrence_id.rfind("/")
            elif occurrence_id.startswith("SFT"):
                index = occurrence_id.find(":")
            else:
                index = occurrence_id.rfind(":")
            
            return [occurrence_id[:index+1], occurrence_id[index+1:]]
            
        split_id = occurrence_id.apply(split_id)

        # Extract the URN prefix and id from the split OccurrenceId column
        urn_prefix = split_id.apply(lambda x: x[0])
        number = split_id.apply(lambda x: x[1])
      
        # Map the URN prefix to the corresponding id
        urn_id = urn_prefix.map(urn_mapping)
        obs_id = urn_id.astype(str) + number.astype(str)
                
        return obs_id



    # Transform observation data to match database columns
    def transform_observations(self, data):
        print("Starting data transformation...")
        
        # Read the GeoJson file into a GeoDataFrame
        gdf = gpd.read_file(data)

        # # Calculate the number of batches
        # num_batches = int(len(gdf) / batch_size) + 1

        # # Create an empty DataFrame to store the transformed data
        # df_full = pd.DataFrame()
        
        # for i in range(num_batches):
        #     print(f"Processing batch {i+1} of {num_batches}...")
        #     start = i * batch_size
        #     end = (i + 1) * batch_size

        # Extract the necessary data from the GeoDataFrame        
        df = pd.DataFrame({
            "id": self.generate_pk(data).astype(str),
            "start_date": gdf["StartDate"],
            "end_date": gdf["EndDate"],
            "position": gdf["geometry"],
            "taxon_id": gdf["DyntaxaTaxonId"],
            "organism_quantity": gdf["OrganismQuantityInt"].fillna(1).astype(int)
        })

        # Set the display options
        # pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', None)
        
        # df_full = pd.concat([df_full, df], ignore_index=True)
        print(df)
        
        return df
    
    # Transform taxa data to match database columns
    def transform_taxa(data):
        with open(data, "r") as f:
            data_dict = json.load(f)
        
        #print(data_dict)
        taxa = data_dict["natureConservationListTaxa"][0]["taxonInformation"]

        # Convert the taxonInformation list into a DataFrame
        df = pd.DataFrame(taxa)
        print(df)

        # Rename the columns
        df = df.rename(columns={
            "id": "id",
            "scientificname": "scientific_name",
            "swedishname": "swedish_name",
            "englishname": "english_name"
        })
        print(df)
        return df

    # FIX: Not finished
    def get_gridid(self, y, x):
        session = self.get_session()
        try:
            stmt = text("""
                SELECT id
                FROM tiles
                WHERE ST_Contains(geometry, ST_SetSRID(ST_Point(:x, :y, :z), 4326))
            """)
            result = session.execute(stmt, {"lat": y, "lon": x})
            return result[0] if result else None
        except:
            session.rollback()
            raise
        finally:
            session.close()



    # Takes transform_data df as input and adds gridId column
    # FIX: Not finished
    def add_gridid(self, df):
        df["gridId"] = df.apply(lambda row: self.get_gridid(row["latitude"], row["longitude"]), axis=1)
        return df


######################################
### Methods for table manipulation ###
######################################


    # Unfinished method for configuring partitioning on the tile_obs_count table
    def Partitioning_Tile_Obs_Count(self):
        # Create an engine
        engine = create_engine('postgresql://user:password@localhost/dbname')

        # Execute raw SQL commands
        with engine.begin() as connection:
            connection.execute(text("""
                CREATE TABLE tile_obs_count (
                    id INTEGER,
                    tile_id INTEGER,
                    zoom_level INTEGER,
                    taxon_id INTEGER,
                    obs_date DATE,
                    obs_count INTEGER
                ) PARTITION BY LIST (taxon_id, zoom_level);
            """))

        # After defining the table, create the partitions
        for i in range(0, 20):  # Assuming zoom levels from 0 to 19
            for j in range(1, 501):  # Assuming taxonId from 1 to 500
                with engine.begin() as connection:
                    connection.execute(text(f"""
                        CREATE TABLE tile_obs_count_{i}_{j} PARTITION OF tile_obs_count 
                        FOR VALUES IN ({i}, {j});
                    """))



    # Populates the observations table with data from a GeoJson file
    # FIX: Not finished
    def populate_observations(self, data):
        db = self(os.environ["DATABASE_URL"])
        session = db.get_session()
        conn = session.connection().connection
        #cur = conn.cursor()

        # CHANGE: File path when populating with whole dataset
        transformed_data = self.transform_observations(self, data)

        transformed_data['position'] = transformed_data['position'].apply(lambda geom: WKTElement(geom.wkt, srid=4326))
        
        # next(f) # Skip the header row.
        transformed_data.to_sql('observations', session.bind, if_exists='append', index=False, dtype={'position': Geometry('POINT', srid=4326)})
        conn.commit()

        session.close()



    # Populates the taxa table with data from a JSON file
    def populate_taxa(self, data):
        db = self(os.environ["DATABASE_URL"])
        session = db.get_session()
        conn = session.connection().connection
        #cur = conn.cursor()

        transformed_data = self.transform_taxa(data)
        transformed_data.to_sql("taxa", session.bind, if_exists='append', index=False)
        conn.commit()

        session.close()

################################
### Add query functions here ###
################################

    def acquire_sweden_geometry(self):
        session = self.get_session()
        sql = text("SELECT ST_AsBinary(geom) as geom FROM polygon;")
        result = session.execute(sql).fetchone()
        session.close()

        binary_geom = result['geom']

        geometry = loads(binary_geom)

        # Convert to a GeoJSON-like dictionary
        geojson_geometry = mapping(geometry)

        # Serialize to a GeoJSON string
        geojson_string = json.dumps({
            "type": "Feature",
            "geometry": geojson_geometry
        })

        return geojson_string


    # Functions to create and update database
    def post_taxa(taxa):
        pass



    def post_observations(observations):
        pass



    # Mock code for retrieving the source url of an observation (e.g. Artportalen, iNaturalist, etc.)
    # Depends on how urn info is stored in the database
    def external_obs_link():
        pass
        # # Unsure if it's better to define the mapping here or as a class variable
        # urn_to_url_mapping = {
        #     'urn:Isid:artportalen.se:Sighting:': 'https://artportalen.se/Sighting/',
        #     'urn:Isid:inaturalist.org:observation:': 'https://www.inaturalist.org/observations/',
        #     # Add more mappings here
        # }    

        # for 'urn:Isid:' in column(observations.id):
        #     if 'urn:Isid:' == 'artportalen.se:Sighting:':
        #         link = urn_to_url_mapping.get('urn:Isid:artportalen.se:Sighting:') + observations.id
        #     elif 'urn:Isid:' == 'inaturalist.org:observation:':
        #         link = urn_to_url_mapping.get('urn:Isid:inaturalist.org:observation:') + observations.id
    


    def observations_in_df(self, model, filters):
        observations = self.query(model, filters=filters)

        data = []
        for obs in observations:
            data.append({
                "longitude": obs.longitude,
                "latitude": obs.latitude,
            })

        df = pd.DataFrame(data)
        return df    



    def get_unique_species_for_dropdown(self, model):
        session = self.get_session()
        try:
            query = session.query(model.swedish_name).filter(
            model.scientific_name.like('% %'),
            model.swedish_name.isnot(None)
        ).distinct()
            result = [row.swedish_name for row in query.all()]
        except Exception as e:
            print(f"An error occurred: {e}")
            result = None
        finally:
            session.close()
        return result

    def get_taxon_id(self, swedish_name):
        session = self.get_session()
        try:
            # Query the ID from Taxa table where the Swedish name matches
            result = session.query(Taxa.id).filter(Taxa.swedish_name == swedish_name).first()
        except Exception as e:
            print(f"An error occurred: {e}")
            result = None
        finally:
            session.close()

        # Return the ID if the result is found, otherwise return None
        return result.id if result else None
