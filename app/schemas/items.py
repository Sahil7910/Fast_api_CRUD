from pydantic import BaseModel
from datetime import date

class ItemCreate(BaseModel):
    name: str
    email: str
    item_name: str
    quantity: int
    expiry_date: date

class ItemUpdate(BaseModel):
    name: str
    email: str
    item_name: str
    quantity: int
    expiry_date: date
