"""
Migrate In-Memory Data to MongoDB Atlas
This script transitions PeopleRate from in-memory storage to MongoDB Atlas
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.database import connect_to_mongo, close_mongo_connection, init_sample_data, get_database_stats
from app.models.mongodb_models import User, Person, Review
from dotenv import load_dotenv

load_dotenv()


async def migrate():
    """Perform migration from in-memory to MongoDB"""
    
    print("=" * 70)
    print("🚀 PeopleRate: Migration to MongoDB Atlas")
    print("=" * 70)
    print()
    
    # Step 1: Connect to MongoDB
    print("📡 Step 1: Connecting to MongoDB Atlas...")
    try:
        await connect_to_mongo()
        print("   ✅ Connected successfully")
    except Exception as e:
        print(f"   ❌ Failed to connect: {e}")
        print("\n⚠️  Migration aborted. Please fix connection issues and try again.")
        print("   See: docs/MONGODB_ATLAS_SETUP.md for help")
        return False
    
    print()
    
    # Step 2: Check existing data
    print("📊 Step 2: Checking existing data...")
    stats = await get_database_stats()
    
    if stats and sum(stats.values()) > 0:
        print("   ⚠️  Database already contains data:")
        for collection, count in stats.items():
            if count > 0:
                print(f"      - {collection}: {count} documents")
        
        print()
        response = input("   ⚠️  Clear existing data and reimport? (yes/no): ")
        
        if response.lower() not in ['yes', 'y']:
            print("   ❌ Migration cancelled by user")
            await close_mongo_connection()
            return False
        
        # Clear existing data
        print("   🗑️  Clearing existing data...")
        await User.delete_all()
        await Person.delete_all()
        await Review.delete_all()
        print("   ✅ Existing data cleared")
    else:
        print("   ✅ Database is empty, ready for migration")
    
    print()
    
    # Step 3: Initialize sample data
    print("🌱 Step 3: Importing sample data...")
    try:
        await init_sample_data()
        print("   ✅ Sample data imported successfully")
    except Exception as e:
        print(f"   ❌ Failed to import data: {e}")
        await close_mongo_connection()
        return False
    
    print()
    
    # Step 4: Verify migration
    print("🔍 Step 4: Verifying migration...")
    stats = await get_database_stats()
    
    print("   📊 Database now contains:")
    print("   " + "-" * 40)
    for collection, count in stats.items():
        status = "✅" if count > 0 else "⚠️"
        print(f"   {status} {collection:20} : {count:5} documents")
    print("   " + "-" * 40)
    
    total = sum(stats.values())
    print(f"   📈 TOTAL: {total} documents")
    
    print()
    
    # Step 5: Summary
    print("=" * 70)
    print("✅ MIGRATION COMPLETE!")
    print("=" * 70)
    print()
    print("🎉 Your PeopleRate platform is now using MongoDB Atlas!")
    print()
    print("📝 What was migrated:")
    print(f"   ✅ {stats['users']} sample users with authentication")
    print(f"   ✅ {stats['persons']} person profiles (including 2 Sasikalas)")
    print(f"   ✅ {stats['reviews']} reviews with ratings")
    print()
    print("🔐 Test Accounts:")
    print("   Email: john.reviewer@email.com")
    print("   Username: TechReviewer2024")
    print("   Password: password123")
    print()
    print("   Email: sarah.manager@email.com")
    print("   Username: ProjectManager_Pro")
    print("   Password: password123")
    print()
    print("🚀 Next Steps:")
    print("   1. Start server: uvicorn main:app --reload")
    print("   2. Visit: http://localhost:8000")
    print("   3. Login with test account")
    print("   4. Try NLP search: 'sasikala who is into consulting'")
    print()
    print("📊 View your data:")
    print("   - MongoDB Atlas Dashboard: https://cloud.mongodb.com/")
    print("   - Browse Collections → users, persons, reviews")
    print()
    print("✅ Week 1 Task 1: Database Migration - COMPLETE!")
    print("   Next: Email Verification (Week 2)")
    print()
    
    await close_mongo_connection()
    return True


if __name__ == "__main__":
    success = asyncio.run(migrate())
    sys.exit(0 if success else 1)
