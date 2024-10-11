import motor.motor_asyncio

# Local MongoDB connection string
MONGO_DETAILS = "mongodb://localhost:27017"

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

# Access your local database
database = client.myappdb

# Define collections
items_collection = database.get_collection("items")
clock_in_collection = database.get_collection("user_clock_in_records")
