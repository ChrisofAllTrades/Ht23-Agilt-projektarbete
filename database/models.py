# FIX: Remove unused imports
from geoalchemy2 import Geometry
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, LargeBinary, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Taxa(Base):
    __tablename__ = "taxa"

    id = Column(Integer, primary_key=True)
    scientific_name = Column(String, nullable=False)
    swedish_name = Column(String)
    english_name = Column(String)
    observation = relationship("Observations", backref="taxa")
    tile_obs_count = relationship("Tile_Obs_Count", backref="taxa")
    # taxonCategory = Column()
    # FIX: Add taxon hierarchy id

    def __repr__(self):
        return f"<Taxa(id={self.id}, scientific_name={self.scientific_name}, swedish_name={self.swedish_name}, english_name={self.english_name})>"

class Observations(Base):
    __tablename__ = "observations"

    id = Column(String, primary_key=True)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    position = Column(Geometry(geometry_type='POINT', srid=4326))
    taxon_id = Column(Integer, ForeignKey("taxa.id"))
    organism_quantity = Column(Integer)

    def __repr__(self): 
        return f"<Observations(id={self.id}, start_date={self.start_date}, end_date={self.end_date}, position={self.position}, taxon_id={self.taxon_id}, organism_quantity={self.organism_quantity})>"

class Polygon(Base):
    __tablename__ = "polygon"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    geom = Column(Geometry(geometry_type='MULTIPOLYGON', srid=4326))
    geom_3857 = Column(Geometry(geometry_type='MULTIPOLYGON', srid=3857))

    def __repr__(self):
        return f"<Polygon(id={self.id}, name={self.name}, geom={self.geom}, geom_3857={self.geom_3857})>"

class Square_Grid(Base):
    __tablename__ = "square_grid"
    
    id = Column(Integer, primary_key=True)
    geom = Column(Geometry(geometry_type='POLYGON', srid=3857))
    zoom_level = Column(Integer)
    tile_obs_count = relationship("Tile_Obs_Count", backref="square_grid")
    def __repr__(self):
        return f"<Square_Grid(id={self.id}, geom={self.geom}, zoom_level={self.zoom_level})>"

class Tile_Obs_Count(Base):
    __tablename__ = "tile_obs_count"
    
    id = Column(Integer, primary_key=True)
    tile_id = Column(Integer, ForeignKey("square_grid.id"))
    taxon_id = Column(Integer, ForeignKey("taxa.id"))
    obs_date = Column(DateTime)
    obs_count = Column(Integer)
    
def __repr__(self):
    return f"<Tile_Obs_Count(id={self.id}, tile_id={self.tile_id}, taxon_id={self.taxon_id}, obs_date={self.obs_date}, obs_count={self.obs_count})>"