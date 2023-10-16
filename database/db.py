from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

##########################################
### Database class and query functions ###
##########################################

class Database:
    def __init__(self, database_uri):
        self.engine = create_engine(database_uri)
        self.Session = sessionmaker(bind=self.engine)

    def get_session(self):
        return self.Session()

    def query(self, model):
        session = self.get_session()
        result = session.query(model).all()
        session.close()
        return result
    
    def setup(self):
        Base.metadata.create_all(self.engine)

################################
### Add query functions here ###
################################

# Functions to create and update database
def post_taxa(taxa):
    pass

def post_observations(observations):
    pass