from sqlalchemy import Column, Integer, Text

from project.utils.base_model import Base


class CityModel(Base):
    __tablename__ = 'cities'
    __table_args__ = {'schema': 'public'}

    id = Column(Integer, primary_key=True, server_default="nextval('cities_id_seq'::regclass)")
    name = Column(Text, nullable=False)