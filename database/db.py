from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, load_only
from database.models import Base, Observations, Taxa
import pandas as pd
# Test-imports
import os


##########################################
### Database class and query functions ###
##########################################

class fenologikDb:
    def __init__(self, database_uri):
        self.engine = create_engine(database_uri, echo=True)
        self.Session = sessionmaker(bind=self.engine)

    def get_session(self):
        return self.Session()

    def query(self, model, filters=None):
        session = self.get_session()
        query = session.query(model)

        if filters:
            query = query.filter(*filters)

        result = query.all()
        session.close()
        return result

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

################################
### Add query functions here ###
################################

    # Functions to create and update database
    def post_taxa(taxa):
        pass

    def post_observations(observations):
        pass

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