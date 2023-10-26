from sqlalchemy import Column, Integer, String, Float, DateTime, Sequence, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Taxa(Base):
    __tablename__ = 'taxa'

    id = Column(Integer, primary_key=True)
    scientificName = Column(String, nullable=False)
    swedishName = Column(String)
    englishName = Column(String)
    observation = relationship('Observations', backref='taxa')
    # FIX: Add taxon hierarchy id

    def __repr__(self):
        return f"<Taxa(id={self.id}, scientificName={self.scientificName}, swedishName={self.swedishName}, englishName={self.englishName})>"

class Observations(Base):
    __tablename__ = 'observations'

    id = Column(Integer, Sequence('observations_id_seq'), primary_key=True)
    startDate = Column(DateTime)
    endDate = Column(DateTime)
    latitude = Column(Float)
    longitude = Column(Float)
    taxonId = Column(Integer, ForeignKey('taxa.id'))

    def __repr__(self):
        return f"<Observations(id={self.id}, startDate={self.startDate}, endDate={self.endDate}, latitude={self.latitude}, longitude={self.longitude})>"