"""
MongoDB Database Connection using Beanie ODM
Provides connection management and initialization for MongoDB Atlas
"""

import os
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from dotenv import load_dotenv
import logging

# Import models
from app.models.mongodb_models import (
    User, Person, Review, Notification, 
    Subscription, FlaggedContent
)

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class Database:
    """Database connection manager"""
    client: AsyncIOMotorClient = None

db = Database()


async def connect_to_mongo():
    """
    Initialize MongoDB connection and Beanie ODM
    Connects to MongoDB Atlas or local MongoDB instance
    """
    mongodb_url = os.getenv("MONGODB_URL")
    database_name = os.getenv("DATABASE_NAME", "peopleRate_db")
    
    if not mongodb_url:
        raise ValueError("MONGODB_URL environment variable is not set")
    
    try:
        # Create Motor client
        db.client = AsyncIOMotorClient(mongodb_url)
        
        # Test connection
        await db.client.admin.command('ping')
        logger.info(f"✅ Successfully connected to MongoDB")
        
        # Initialize Beanie with document models
        await init_beanie(
            database=db.client[database_name],
            document_models=[
                User,
                Person,
                Review,
                Notification,
                Subscription,
                FlaggedContent
            ]
        )
        
        logger.info(f"✅ Beanie ODM initialized with database: {database_name}")
        logger.info("� Collections: users, persons, reviews, notifications, subscriptions, flagged_content")
        
        # Create indexes (Beanie handles this automatically based on model definitions)
        logger.info("🔧 Creating indexes...")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to connect to MongoDB: {e}")
        logger.error("💡 Please check your MONGODB_URL in .env file")
        logger.error("💡 Make sure MongoDB Atlas is accessible and credentials are correct")
        raise


async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        logger.info("✅ MongoDB connection closed")


async def init_sample_data():
    """
    Initialize sample data for development/testing
    Only runs if collections are empty
    """
    try:
        # Check if data already exists
        user_count = await User.count()
        if user_count > 0:
            logger.info(f"📊 Database already has {user_count} users. Skipping sample data initialization.")
            return
        
        logger.info("🌱 Initializing sample data...")
        
        # Import sample data initialization
        from scripts.init_sample_data import create_sample_data
        await create_sample_data()
        
        logger.info("✅ Sample data initialized successfully")
        
    except ImportError:
        logger.warning("⚠️ Sample data script not found. Skipping initialization.")
    except Exception as e:
        logger.error(f"❌ Failed to initialize sample data: {e}")


# Helper function to get database statistics
async def get_database_stats():
    """Get database statistics"""
    try:
        stats = {
            "users": await User.count(),
            "persons": await Person.count(),
            "reviews": await Review.count(),
            "notifications": await Notification.count(),
            "subscriptions": await Subscription.count(),
            "flagged_content": await FlaggedContent.count(),
        }
        return stats
    except Exception as e:
        logger.error(f"Failed to get database stats: {e}")
        return None