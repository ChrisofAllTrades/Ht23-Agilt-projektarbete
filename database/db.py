from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from database.models import Base

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

################################
### Add query functions here ###
################################

    # Functions to create and update database
    def post_taxa(taxa):
        pass

    def post_observations(observations):
        pass