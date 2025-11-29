"""
Test MongoDB Atlas Connection
Quick script to verify your MongoDB Atlas setup is working
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.database import connect_to_mongo, close_mongo_connection, get_database_stats
from dotenv import load_dotenv
import os

load_dotenv()


async def test_connection():
    """Test MongoDB connection and display stats"""
    
    print("=" * 60)
    print("🧪 Testing MongoDB Atlas Connection")
    print("=" * 60)
    
    # Check if MONGODB_URL is set
    mongodb_url = os.getenv("MONGODB_URL")
    if not mongodb_url:
        print("❌ ERROR: MONGODB_URL not set in .env file")
        print("\n📝 Please follow these steps:")
        print("1. Open .env file")
        print("2. Set MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/")
        print("3. Replace username, password, and cluster with your MongoDB Atlas credentials")
        return False
    
    # Mask password in URL for display
    display_url = mongodb_url
    if "@" in display_url:
        parts = display_url.split("@")
        credentials = parts[0].split("//")[1]
        if ":" in credentials:
            username = credentials.split(":")[0]
            display_url = display_url.replace(credentials, f"{username}:****")
    
    print(f"\n📡 Connecting to: {display_url}")
    print(f"🗄️  Database: {os.getenv('DATABASE_NAME', 'peopleRate_db')}")
    print()
    
    try:
        # Attempt connection
        await connect_to_mongo()
        
        print("\n✅ CONNECTION SUCCESSFUL!")
        print()
        
        # Get database statistics
        print("📊 Database Statistics:")
        print("-" * 40)
        stats = await get_database_stats()
        
        if stats:
            for collection, count in stats.items():
                print(f"   {collection:20} : {count:5} documents")
            
            total = sum(stats.values())
            print("-" * 40)
            print(f"   {'TOTAL':20} : {total:5} documents")
        else:
            print("   No statistics available (empty database)")
        
        print()
        print("=" * 60)
        print("✅ MongoDB Atlas is properly configured!")
        print("=" * 60)
        print()
        print("🎉 Next steps:")
        print("   1. Run: python scripts/migrate_to_mongodb.py  (to add sample data)")
        print("   2. Run: uvicorn main:app --reload  (to start the server)")
        print()
        
        await close_mongo_connection()
        return True
        
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\n📝 Please check your .env file:")
        print("   - MONGODB_URL should be set")
        print("   - Format: mongodb+srv://username:password@cluster.mongodb.net/")
        return False
        
    except Exception as e:
        print(f"\n❌ CONNECTION FAILED!")
        print(f"   Error: {str(e)}")
        print()
        print("🔧 Troubleshooting steps:")
        print("   1. Check your internet connection")
        print("   2. Verify MongoDB Atlas cluster is running")
        print("   3. Check IP address is whitelisted in MongoDB Atlas")
        print("   4. Verify username and password are correct")
        print("   5. Ensure password is URL encoded (special characters)")
        print()
        print("📚 For detailed help, see: docs/MONGODB_ATLAS_SETUP.md")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_connection())
    sys.exit(0 if success else 1)
