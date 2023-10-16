from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# To do: Create table for square grid

Base = declarative_base()

class Taxa(Base):
    __tablename__ = 'taxa'

    id = Column(Integer, primary_key=True)
    scientificName = Column(String, nullable=False)
    swedishName = Column(String)
    englishName = Column(String)
    observation = relationship('Observations', backref='taxa')
    # taxonCategory = Column()
    # FIX: Add taxon hierarchy id

    def __repr__(self):
        return f"<Taxa(id={self.id}, scientificName={self.scientificName}, swedishName={self.swedishName}, englishName={self.englishName})>"

class Observations(Base):
    __tablename__ = 'observations'

    id = Column(String, primary_key=True)
    startDate = Column(DateTime)
    endDate = Column(DateTime)
    latitude = Column(Float)
    longitude = Column(Float)
    gridId = Column(Integer)
    taxonId = Column(Integer, ForeignKey('taxa.id'))
    organismQuantity = Column(Integer)

    def __repr__(self): 
        return f"<Observations(id={self.id}, startDate={self.startDate}, endDate={self.endDate}, latitude={self.latitude}, longitude={self.longitude}, organismQuantity={self.organismQuantity})>"
