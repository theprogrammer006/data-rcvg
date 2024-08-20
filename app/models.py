from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    plants = relationship("Plant", back_populates="user")

class Plant(Base):
    __tablename__ = "plants"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    plant_name = Column(String, nullable=False)
    plant_type = Column(String, nullable=False)
    user = relationship("User", back_populates="plants")
    pot = relationship("Pot", uselist=False, back_populates="plant")

class Pot(Base):
    __tablename__ = "pots"
    id = Column(Integer, primary_key=True, index=True)
    plant_id = Column(Integer, ForeignKey("plants.id"))
    pot_name = Column(String, nullable=False)
    plant = relationship("Plant", back_populates="pot")
    sensor_data = relationship("SensorData", back_populates="pot")

class SensorData(Base):
    __tablename__ = "sensor_data"
    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(String, nullable=False)
    pot_id = Column(Integer, ForeignKey("pots.id"))
    moisture = Column(Float, nullable=False)
    light = Column(Float, nullable=False)
    temperature = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    pot = relationship("Pot", back_populates="sensor_data")
