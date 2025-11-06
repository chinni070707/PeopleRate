import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Database:
    client: AsyncIOMotorClient = None
    database = None

db = Database()

async def get_database():
    return db.database

async def connect_to_mongo():
    """Create database connection"""
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    database_name = os.getenv("DATABASE_NAME", "peopleRate_db")
    
    db.client = AsyncIOMotorClient(mongodb_url)
    db.database = db.client[database_name]
    
    # Test the connection
    try:
        await db.client.admin.command('ping')
        print(f"✅ Successfully connected to MongoDB at {mongodb_url}")
        print(f"📊 Using database: {database_name}")
    except Exception as e:
        print(f"⚠️ Warning: Failed to connect to MongoDB: {e}")
        print("💡 Note: MongoDB is not required for testing the API structure.")
        print("💡 Install MongoDB locally or use MongoDB Atlas for full functionality.")
        # Don't raise the exception in development
        # raise e

async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        print("MongoDB connection closed")

# Collection helpers
async def get_user_collection():
    database = await get_database()
    return database.users

async def get_person_collection():
    database = await get_database()
    return database.persons

async def get_review_collection():
    database = await get_database()
    return database.reviews