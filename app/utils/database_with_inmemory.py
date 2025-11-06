import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import pymongo_inmemory

# Load environment variables
load_dotenv()

class Database:
    client: AsyncIOMotorClient = None
    database = None
    use_inmemory = False

db = Database()

async def get_database():
    return db.database

async def connect_to_mongo():
    """Create database connection - tries real MongoDB first, falls back to in-memory"""
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    database_name = os.getenv("DATABASE_NAME", "peopleRate_db")
    
    # Try to connect to real MongoDB first
    try:
        db.client = AsyncIOMotorClient(mongodb_url, serverSelectionTimeoutMS=5000)
        await db.client.admin.command('ping')
        db.database = db.client[database_name]
        print(f"✅ Successfully connected to MongoDB at {mongodb_url}")
        print(f"📊 Using database: {database_name}")
        return
    except Exception as e:
        print(f"⚠️ Could not connect to MongoDB: {e}")
        print("🔄 Falling back to in-memory MongoDB for testing...")
    
    # Fall back to in-memory MongoDB
    try:
        # Start in-memory MongoDB instance
        mongod_process = pymongo_inmemory.Mongod()
        inmemory_uri = mongod_process.uri
        
        db.client = AsyncIOMotorClient(inmemory_uri)
        db.database = db.client[database_name]
        db.use_inmemory = True
        
        # Test the connection
        await db.client.admin.command('ping')
        print(f"✅ Successfully connected to in-memory MongoDB")
        print(f"📊 Using in-memory database: {database_name}")
        print("💡 This is great for testing - data will be lost when app stops")
        
    except Exception as e:
        print(f"❌ Failed to start in-memory MongoDB: {e}")
        print("💡 Please install MongoDB or use MongoDB Atlas")
        # Set a dummy client for API structure testing
        db.client = None
        db.database = None

async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        print("MongoDB connection closed")

# Collection helpers
async def get_user_collection():
    database = await get_database()
    if database is None:
        return None
    return database.users

async def get_person_collection():
    database = await get_database()
    if database is None:
        return None
    return database.persons

async def get_review_collection():
    database = await get_database()
    if database is None:
        return None
    return database.reviews