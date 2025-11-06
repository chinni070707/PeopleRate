"""
MongoDB Setup Guide for PeopleRate

This script provides multiple options to get MongoDB running for PeopleRate.
"""

import subprocess
import sys
import os
import webbrowser
from pathlib import Path

def print_section(title):
    print(f"\n{'='*50}")
    print(f" {title}")
    print(f"{'='*50}")

def run_command(cmd, description):
    print(f"\n🔄 {description}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Success: {description}")
            return True
        else:
            print(f"❌ Failed: {description}")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Exception during {description}: {e}")
        return False

def check_mongodb_installed():
    """Check if MongoDB is already installed"""
    try:
        result = subprocess.run("mongod --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ MongoDB is already installed!")
            print(f"Version info: {result.stdout.split()[2]}")
            return True
    except:
        pass
    
    # Check if MongoDB service exists
    try:
        result = subprocess.run('sc query "MongoDB"', shell=True, capture_output=True, text=True)
        if "RUNNING" in result.stdout:
            print("✅ MongoDB service is running!")
            return True
    except:
        pass
    
    return False

def install_mongodb_community():
    """Install MongoDB Community Edition"""
    print_section("Installing MongoDB Community Edition")
    
    print("📥 Downloading MongoDB installer...")
    
    # Download MongoDB
    download_url = "https://fastdl.mongodb.org/windows/mongodb-windows-x86_64-8.0.1-signed.msi"
    installer_path = os.path.join(os.environ['TEMP'], 'mongodb-installer.msi')
    
    download_cmd = f'powershell -Command "Invoke-WebRequest -Uri \'{download_url}\' -OutFile \'{installer_path}\'"'
    
    if run_command(download_cmd, "Downloading MongoDB installer"):
        print(f"📦 Installer downloaded to: {installer_path}")
        
        # Run installer
        print("\n🔧 Running MongoDB installer...")
        print("⚠️ Please follow the installation wizard:")
        print("   1. Choose 'Complete' installation")
        print("   2. Install MongoDB as a Service")
        print("   3. Install MongoDB Compass (optional but recommended)")
        
        install_cmd = f'msiexec /i "{installer_path}" /qr'
        subprocess.Popen(install_cmd, shell=True)
        
        print("✅ MongoDB installation started!")
        print("⏳ Please wait for the installation to complete...")
        return True
    
    return False

def setup_mongodb_atlas():
    """Guide for setting up MongoDB Atlas (cloud)"""
    print_section("MongoDB Atlas (Cloud) Setup")
    
    print("🌐 MongoDB Atlas is a cloud-hosted MongoDB service")
    print("✅ No local installation required")
    print("✅ Free tier available")
    print("✅ Automatic backups and scaling")
    
    print("\n📋 Steps to set up MongoDB Atlas:")
    print("1. Go to https://www.mongodb.com/atlas")
    print("2. Click 'Start Free'")
    print("3. Create an account")
    print("4. Create a new cluster (choose M0 Sandbox for free tier)")
    print("5. Create a database user")
    print("6. Add your IP address to the allowlist")
    print("7. Get the connection string")
    
    print("\n🔗 Opening MongoDB Atlas website...")
    webbrowser.open("https://www.mongodb.com/atlas/register")
    
    print("\n📝 After setup, update your .env file:")
    print("MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/")
    print("DATABASE_NAME=peopleRate_db")

def start_mongodb_service():
    """Start MongoDB service"""
    print_section("Starting MongoDB Service")
    
    # Try to start MongoDB service
    if run_command('net start MongoDB', "Starting MongoDB service"):
        return True
    
    # Alternative: try to start mongod directly
    print("\n🔄 Trying to start mongod directly...")
    mongod_path = "C:\\Program Files\\MongoDB\\Server\\8.0\\bin\\mongod.exe"
    data_path = "C:\\data\\db"
    
    # Create data directory if it doesn't exist
    Path(data_path).mkdir(parents=True, exist_ok=True)
    
    cmd = f'"{mongod_path}" --dbpath "{data_path}"'
    print(f"Running: {cmd}")
    print("⚠️ This will run MongoDB in the foreground. Keep this terminal open.")
    
    try:
        subprocess.Popen(cmd, shell=True)
        print("✅ MongoDB started!")
        return True
    except Exception as e:
        print(f"❌ Failed to start MongoDB: {e}")
        return False

def test_connection():
    """Test MongoDB connection"""
    print_section("Testing MongoDB Connection")
    
    try:
        import pymongo
        client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print("✅ Successfully connected to MongoDB!")
        
        # Test database operations
        db = client.test_database
        collection = db.test_collection
        
        # Insert a test document
        test_doc = {"test": "PeopleRate setup", "status": "working"}
        result = collection.insert_one(test_doc)
        print(f"✅ Test document inserted with ID: {result.inserted_id}")
        
        # Clean up
        collection.delete_one({"_id": result.inserted_id})
        print("✅ Database operations working correctly!")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def main():
    print_section("PeopleRate MongoDB Setup")
    
    print("🎯 This script will help you set up MongoDB for PeopleRate")
    print("\nOptions:")
    print("1. Check if MongoDB is already installed")
    print("2. Install MongoDB Community Edition locally")
    print("3. Set up MongoDB Atlas (cloud)")
    print("4. Start MongoDB service")
    print("5. Test MongoDB connection")
    print("6. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == "1":
                if check_mongodb_installed():
                    print("✅ MongoDB is ready to use!")
                else:
                    print("❌ MongoDB not found. Choose option 2 or 3 to install.")
                    
            elif choice == "2":
                install_mongodb_community()
                
            elif choice == "3":
                setup_mongodb_atlas()
                
            elif choice == "4":
                start_mongodb_service()
                
            elif choice == "5":
                test_connection()
                
            elif choice == "6":
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please enter 1-6.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break

if __name__ == "__main__":
    main()