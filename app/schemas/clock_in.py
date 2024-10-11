from pydantic import BaseModel

class ClockInCreate(BaseModel):
    email: str
    location: str

class ClockInUpdate(BaseModel):
    email: str
    location: str
