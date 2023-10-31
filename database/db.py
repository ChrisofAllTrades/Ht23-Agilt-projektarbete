import os

import geopandas as gpd
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import load_only, sessionmaker

from database.models import Base, Observations, Taxa

# To do: Finish methods for assigning gridId to observations
# To do: Add method for processing entire dataset in chunks
# To do: Add method for grouping observations by gridId, taxonId and datetime
#           -  Save to new table with columns gridId, taxonId, datetime, count
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



    # Transform data to match database columns
    def transform_data(self, data):
        gdf = gpd.read_file(data)

        # Extract the necessary data from the GeoDataFrame
        df = pd.DataFrame({
            "id": self.generate_pk(data).astype(str),
            "startDate": gdf["StartDate"],
            "endDate": gdf["EndDate"],
            "latitude": gdf["geometry"].y,
            "longitude": gdf["geometry"].x,
            "taxonId": gdf["DyntaxaTaxonId"],
            "organismQuantity": gdf["OrganismQuantityInt"].fillna(1).astype(int)
        })

        # Set the display options
        # pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', None)
        
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



    # CHANGE: Function name
    # FIX: Not finished
    def populate_database(data):

        db = FenologikDb(os.environ["DATABASE_URL"])
        session = db.get_session()
        conn = session.connection().connection
        cur = conn.cursor()

        # CHANGE: File path when populating with whole dataset
        transformed_data = FenologikDb.transform_data(data)
        # next(f) # Skip the header row.
        transformed_data.to_sql('observations', session.bind, if_exists='append', index=False)
        conn.commit()

        session.close()

################################
### Add query functions here ###
################################


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
            query = session.query(model).distinct(model.swedishName)
            result = [row.swedishName for row in query.all()]
        except Exception as e:
            print(f"An error occurred: {e}")
            result = None
        finally:
            session.close()
        return result
    


    def get_unique_species_for_dropdown_test(self, model):
        try:
            session = self.get_session()
            session.begin()
            query = session.query(model).distinct(model.swedishName)
            results = query.all()

            result = [row.swedishName for row in results]
            session.commit()
        except Exception as e:
            print(f"An error occurred: {e}")
            print(f"Error type: {type(e)}")
            session.rollback()
            result = None
        finally:
            session.close()
        return result



    def get_taxon_id(self, swedish_name):
        session = self.get_session()
        result = session.query(Observations, Taxa).\
                join(Taxa, Observations.taxonId == Taxa.id).\
                filter(Taxa.swedishName == swedish_name).\
                first()
    
        session.close()
    
        if result:
            return result.Taxa.id  # Returnerar taxonid från Taxa-tabellen
        else:
            return None
