from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from database.models import Base
import os

# To do: Clean up class to separate database functions from query functions

##########################################
### Database class and query functions ###
##########################################

class fenologikDb:
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

    def table_id_sequence(self):
        engine = self.engine

        with engine.connect() as conn:
            conn.execute(text("""
                ALTER TABLE observations 
                ALTER COLUMN id 
                SET DEFAULT nextval('observations_id_seq');
            """))

    # CHANGE: Function name
    def populate_database():
        db = fenologikDb(os.environ['DATABASE_URL'])
        session = db.get_session()
        conn = session.connection().connection
        cur = conn.cursor()

        # CHANGE: File path when populating with whole dataset
        with open('testing/observations.csv', 'r') as f:
            next(f) # Skip the header row.
            cur.copy_from(f, 'observations', columns=('startDate', 'endDate', 'latitude', 'longitude', 'taxonId'), sep=',')
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
        # }    

        # for 'urn:Isid:' in column(observations.id):
        #     if 'urn:Isid:' == 'artportalen.se:Sighting:':
        #         link = urn_to_url_mapping.get('urn:Isid:artportalen.se:Sighting:') + observations.id
        #     elif 'urn:Isid:' == 'inaturalist.org:observation:':
        #         link = urn_to_url_mapping.get('urn:Isid:inaturalist.org:observation:') + observations.id