from fastapi import APIRouter,HTTPException,FastAPI
from app.schemas.clock_in import ClockInCreate, ClockInUpdate
from datetime import datetime
from app.services.database import clock_in_collection
from bson import ObjectId
from typing import List, Optional
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient


router = APIRouter()



app = FastAPI()
@router.post("/clock-in")
async def create_clock_in(clock_in: ClockInCreate):
    clock_in_dict = clock_in.dict()
    clock_in_dict["insert_date_time"] = datetime.utcnow()
    result = await clock_in_collection.insert_one(clock_in_dict)
    return {"id": str(result.inserted_id)}


@router.get("/clock-in/{id}")
async def get_clock_in_by_id(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid clock-in ID format")

    clock_in_record = await clock_in_collection.find_one({"_id": ObjectId(id)})
    if clock_in_record is None:
        raise HTTPException(status_code=404, detail="Clock-in record not found")

    clock_in_record["_id"] = str(clock_in_record["_id"])  # Convert ObjectId to string
    return clock_in_record





@router.put("/clock-in/{id}")
async def update_clock_in(id: str, clock_in: ClockInUpdate):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid clock-in ID format")

    clock_in_dict = clock_in.dict(exclude_unset=True)  # Only update provided fields

    result = await clock_in_collection.update_one(
        {"_id": ObjectId(id)}, {"$set": clock_in_dict}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Clock-in record not found or no changes made")

    return {"message": "Clock-in record updated successfully"}


@router.delete("/clock-in/{id}")
async def delete_clock_in(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid clock-in ID format")

    result = await clock_in_collection.delete_one({"_id": ObjectId(id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Clock-in record not found")

    return {"message": "Clock-in record deleted successfully"}


class ClockInRecord(BaseModel):
    email: str



class ClockInRecord(BaseModel):
    email: str
    location: str
    clock_in_time: datetime
