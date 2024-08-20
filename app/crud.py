from sqlalchemy.ext.asyncio import AsyncSession
from .models import User, Plant, Pot, SensorData

async def create_user(db: AsyncSession, user_data):
    db_user = User(username=user_data.username, password_hash=user_data.password_hash, email=user_data.email)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    plant_name = f"{user_data.username}'s {user_data.plant_type}"
    db_plant = Plant(user_id=db_user.id, plant_name=plant_name, plant_type=user_data.plant_type)
    db.add(db_plant)
    await db.commit()
    await db.refresh(db_plant)
    
    pot_name = f"{user_data.username}'s Pot"
    db_pot = Pot(plant_id=db_plant.id, pot_name=pot_name)
    db.add(db_pot)
    await db.commit()
    await db.refresh(db_pot)
    
    return db_user

async def create_sensor_data(db: AsyncSession, sensor_data):
    db_data = SensorData(**sensor_data.dict())
    db.add(db_data)
    await db.commit()
    await db.refresh(db_data)
    return db_data
