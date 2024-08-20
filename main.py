from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from datetime import datetime
import os

app=FASTAPI()
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+asyncpg://user:password@host/dbname')

# Set up database engine and session
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
Base = declarative_base()

# Define the models
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

# Pydantic models for request validation
class UserCreate(BaseModel):
    username: str
    password_hash: str
    email: str
    plant_type: str

class SensorDataCreate(BaseModel):
    sensor_id: str
    pot_id: int
    moisture: float
    light: float
    temperature: float

# Dependency to get a session
async def get_db():
    async with SessionLocal() as session:
        yield session

# API routes
@app.post("/users/", response_model=UserCreate)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # Create the user
    db_user = User(username=user.username, password_hash=user.password_hash, email=user.email)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    # Automatically create a plant and pot associated with the user
    plant_name = f"{user.username}'s {user.plant_type}"
    db_plant = Plant(user_id=db_user.id, plant_name=plant_name, plant_type=user.plant_type)
    db.add(db_plant)
    await db.commit()
    await db.refresh(db_plant)
    
    # Automatically create a pot associated with the plant
    pot_name = f"{user.username}'s Pot"
    db_pot = Pot(plant_id=db_plant.id, pot_name=pot_name)
    db.add(db_pot)
    await db.commit()
    await db.refresh(db_pot)
    
    return db_user

@app.post("/sensor-data/", response_model=SensorDataCreate)
async def create_sensor_data(sensor_data: SensorDataCreate, db: AsyncSession = Depends(get_db)):
    db_data = SensorData(**sensor_data.dict())
    db.add(db_data)
    await db.commit()
    await db.refresh(db_data)
    return db_data

@app.get("/user-data/{user_id}")
async def get_user_data(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        "SELECT sensor_data.* FROM sensor_data JOIN pots ON sensor_data.pot_id = pots.id "
        "JOIN plants ON pots.plant_id = plants.id WHERE plants.user_id = :user_id "
        "ORDER BY sensor_data.timestamp DESC LIMIT 10",
        {"user_id": user_id}
    )
    data = result.fetchall()
    return data

@app.get("/admin-data/")
async def get_admin_data(db: AsyncSession = Depends(get_db)):
    result = await db.execute("SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 100")
    data = result.fetchall()
    return data

# Ensure tables are created in the database
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
