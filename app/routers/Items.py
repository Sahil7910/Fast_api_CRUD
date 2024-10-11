from fastapi import APIRouter,HTTPException
from app.schemas.items import ItemCreate  # Import Pydantic models from schemas
from app.services.database import items_collection
from datetime import datetime, date
from bson import ObjectId
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient


router = APIRouter()

@router.post("/items")
async def create_item(item: ItemCreate):
    try:
        item_dict = item.dict()
        item_dict["expiry_date"] = datetime.combine(item.expiry_date, datetime.min.time())
        item_dict["insert_date"] = datetime.utcnow()  # Automatically add insert date

        result = await items_collection.insert_one(item_dict)
        return {"id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/items/{id}")
async def get_item_by_id(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid item ID format")

    item = await items_collection.find_one({"_id": ObjectId(id)})
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    item["_id"] = str(item["_id"])  # Convert ObjectId to string
    return item

@router.put("/items/{id}")
async def update_item(id: str, item: ItemCreate):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid item ID format")

    item_dict = item.dict()
    item_dict["expiry_date"] = datetime.combine(item.expiry_date, datetime.min.time())

    result = await items_collection.update_one(
        {"_id": ObjectId(id)}, {"$set": item_dict}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Item not found or no changes made")

    return {"message": "Item updated successfully"}


@router.delete("/items/{id}")
async def delete_item(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid item ID format")

    result = await items_collection.delete_one({"_id": ObjectId(id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")

    return {"message": "Item deleted successfully"}




@router.get("/items/filter")
async def filter_items(
        id: Optional[str] = None,  # Assuming item_id is passed as a query parameter
        email: Optional[str] = None,
        expiry_date: Optional[date] = None,
        insert_date: Optional[date] = None,
        quantity: Optional[int] = None
):
    filter_criteria = {}

    # Debugging: Check if email is received correctly
    print(f"Received email: {email}")

    # Handle the id filter safely
    if id:  # Assuming item_id is passed as a query parameter
        try:
            filter_criteria["_id"] = ObjectId(id)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid item ID format: {str(e)}")

    if email:
        filter_criteria["email"] = email  # Check that 'email' exists in MongoDB
    if expiry_date:
        filter_criteria["expiry_date"] = {"$gt": expiry_date}
    if insert_date:
        filter_criteria["insert_date"] = {"$gt": insert_date}
    if quantity is not None:
        filter_criteria["quantity"] = {"$gte": quantity}

    # Debugging: Log filter criteria for deeper inspection
    print(f"Filter criteria: {filter_criteria}")

    try:
        # Fetching items based on filter criteria
        items = await items_collection.find(filter_criteria).to_list(length=None)
        if not items:
            print("No items found")  # Log if no items were found
            raise HTTPException(status_code=404, detail="No items found matching the criteria")

        # Debugging: Log found items for deeper inspection
        print(f"Found items: {items}")
        return items
    except Exception as e:
        print(f"Error occurred: {str(e)}")  # Log the exact error message
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
