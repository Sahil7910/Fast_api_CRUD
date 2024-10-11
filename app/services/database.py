import motor.motor_asyncio



client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')


db = client['myappdb']
items_collection = db['items']
clock_in_collection = db['user_clock_in_records']


# # Access your local database
# database = client.myappdb
#
# # Define collections
# items_collection = database.get_collection("items")
# clock_in_collection = database.get_collection("user_clock_in_records")




