from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from .database import get_db, Base, engine
from .schemas import UserCreate, SensorDataCreate
from .crud import create_user, create_sensor_data

app = FastAPI()

# Auto-create tables when the app starts
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.post("/users/")
async def create_user_endpoint(user: UserCreate, db: AsyncSession = Depends(get_db)):
    return await create_user(db, user)

@app.post("/sensor-data/")
async def create_sensor_data_endpoint(sensor_data: SensorDataCreate, db: AsyncSession = Depends(get_db)):
    return await create_sensor_data(db, sensor_data)

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
