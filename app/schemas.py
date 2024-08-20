from pydantic import BaseModel

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
