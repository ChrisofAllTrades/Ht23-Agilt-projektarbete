from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
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

    def __repr__(self):
        return f"<Taxa(id={self.id}, scientificName={self.scientificName}, swedishName={self.swedishName}, englishName={self.englishName})>"

class Observations(Base):
    __tablename__ = 'observations'

    id = Column(Integer, primary_key=True)
    taxonId = Column(Integer, ForeignKey('taxa.id'))
    startDate = Column(Date, nullable=False)
    endDate = Column(Date, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    def __repr__(self):
        return f"<Observations(id={self.id}, startDate={self.startDate}, endDate={self.endDate}, latitude={self.latitude}, longitude={self.longitude})>"