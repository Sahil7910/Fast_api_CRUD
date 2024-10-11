from idlelib.query import Query

from fastapi import APIRouter,HTTPException
from app.schemas.items import ItemCreate  # Import Pydantic models from schemas
from app.services.database import items_collection
from datetime import datetime, date
from bson import ObjectId
from typing import Optional


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
    email: Optional[str] = None,
    expiry_date: Optional[date] = None,
    insert_date: Optional[date] = None,
    quantity: Optional[int] = None
):
    # Create a filter dictionary
    filter_criteria = {}

    # Adding filters only if they are provided
    if email:
        filter_criteria["email"] = email
    if expiry_date:
        filter_criteria["expiry_date"] = {"$gt": expiry_date}
    if insert_date:
        filter_criteria["insert_date"] = {"$gt": insert_date}
    if quantity is not None:  # Check for None to handle optional quantity
        filter_criteria["quantity"] = {"$gte": quantity}

    try:
        # Fetching items based on filter criteria
        items = await items_collection.find(filter_criteria).to_list(length=None)
        if not items:
            raise HTTPException(status_code=404, detail="No items found matching the criteria")
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

