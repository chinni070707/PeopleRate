# Quick Start: MongoDB Atlas Migration

## ✅ What We've Set Up

You now have a **production-ready database system** using MongoDB Atlas with Beanie ODM!

### 📦 Installed:
- ✅ `beanie` - Modern MongoDB ODM with Pydantic integration
- ✅ Type-safe models with automatic validation
- ✅ Automatic indexing for fast queries
- ✅ Migration scripts

### 📁 Files Created:

1. **app/models/mongodb_models.py** - Database models
   - User, Person, Review, Notification, Subscription, FlaggedContent
   
2. **app/utils/database.py** - Updated database connection with Beanie

3. **scripts/init_sample_data.py** - Sample data initialization

4. **scripts/test_connection.py** - Connection test script

5. **scripts/migrate_to_mongodb.py** - Full migration script

6. **docs/MONGODB_ATLAS_SETUP.md** - Complete setup guide

---

## 🚀 NEXT STEPS (Do These Now!)

### Step 1: Update Your .env File

Open `.env` and replace the placeholder with your MongoDB Atlas connection string:

```bash
# Get this from MongoDB Atlas dashboard → Connect → Connect your application
MONGODB_URL=mongodb+srv://YOUR_USERNAME:YOUR_PASSWORD@YOUR_CLUSTER.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=peopleRate_db
```

**Important:**
- Replace `YOUR_USERNAME` with your MongoDB Atlas username
- Replace `YOUR_PASSWORD` with your password (**URL encode special characters!**)
- Replace `YOUR_CLUSTER` with your cluster URL

**Example:**
```bash
MONGODB_URL=mongodb+srv://myuser:MyPass123@cluster0.ab1cd.mongodb.net/?retryWrites=true&w=majority
```

### Step 2: Whitelist Your IP in MongoDB Atlas

1. Go to MongoDB Atlas → Network Access
2. Click "Add IP Address"
3. Click "Add Current IP Address" (or "Allow Access from Anywhere" for testing)

### Step 3: Test Connection

```bash
# Activate virtual environment (if not already active)
.\venv\Scripts\Activate.ps1

# Test MongoDB connection
python scripts/test_connection.py
```

**Expected output:**
```
✅ CONNECTION SUCCESSFUL!
📊 Database Statistics:
----------------------------------------
   users                :     0 documents
   persons              :     0 documents
   reviews              :     0 documents
----------------------------------------
```

### Step 4: Run Migration

```bash
python scripts/migrate_to_mongodb.py
```

**This will:**
- ✅ Create all collections with indexes
- ✅ Import 3 sample users
- ✅ Import 5 sample persons (including 2 Sasikalas)
- ✅ Import 3 sample reviews

### Step 5: Update main.py (Important!)

We need to update `main.py` to use the new database system instead of in-memory.

**I'll help you with this next!** Let me know when you've:
1. ✅ Updated .env with your MongoDB Atlas URL
2. ✅ Whitelisted your IP
3. ✅ Tested connection successfully
4. ✅ Run the migration

---

## 🔧 Troubleshooting

### "Can't connect to MongoDB"
- Check internet connection
- Verify IP is whitelisted in MongoDB Atlas
- Check connection string is correct

### "Authentication failed"
- Verify username/password in MongoDB Atlas
- URL encode special characters in password (see docs/MONGODB_ATLAS_SETUP.md)

### "Import errors"
- Make sure you ran: `pip install beanie`
- Restart VS Code/terminal

---

## 📚 What Changed?

### Before (In-Memory):
```python
DATABASE = {
    "users": {},
    "persons": {},
    "reviews": {}
}
```
❌ Data lost on restart  
❌ No validation  
❌ No indexing  
❌ Not scalable

### After (MongoDB Atlas + Beanie):
```python
from app.models.mongodb_models import User

# Type-safe, validated, persistent
user = User(email="test@email.com", username="testuser")
await user.insert()
```
✅ Persistent storage  
✅ Pydantic validation  
✅ Automatic indexes  
✅ Cloud-hosted & scalable  
✅ Automatic backups

---

## 🎯 Benefits You Get:

1. **No Data Loss** - Everything persists in cloud
2. **Fast Queries** - Indexed on name, company, city, email
3. **Type Safety** - Pydantic catches errors before database
4. **Scalability** - MongoDB Atlas scales automatically
5. **Backups** - Automatic backups included
6. **Production Ready** - Used by thousands of companies

---

## 📊 Database Collections:

1. **users** - User accounts
   - Email, username, password (hashed)
   - Profile photo, bio
   - Review count, reputation score
   - Subscription tier

2. **persons** - People being reviewed
   - Name, email, phone
   - Job, company, location
   - 6 social media URLs
   - Skills, education, certifications

3. **reviews** - Reviews about persons
   - Rating (1-5 stars)
   - Comment, title
   - Dimensional ratings
   - Moderation status

4. **notifications** - User notifications
   - New review alerts
   - Profile views
   - Weekly digests

5. **subscriptions** - Premium subscriptions
   - Stripe integration ready
   - Tier management
   - Billing periods

6. **flagged_content** - Moderation queue
   - Report reasons
   - Resolution tracking
   - Admin notes

---

## ✅ Migration Checklist

- [ ] MongoDB Atlas account created
- [ ] Cluster created and running
- [ ] Database user created
- [ ] IP address whitelisted
- [ ] .env updated with connection string
- [ ] `pip install beanie` completed
- [ ] Connection test passed
- [ ] Migration script run successfully
- [ ] Sample data visible in MongoDB Atlas dashboard

---

## 🎉 After Migration

Once migration is complete:

1. Your data persists across restarts
2. You can view data in MongoDB Atlas dashboard
3. Queries are indexed and fast
4. Ready for production deployment
5. **Week 1, Task 1: Database Migration - COMPLETE! ✅**

---

## 📞 Need Help?

- **Setup Guide**: `docs/MONGODB_ATLAS_SETUP.md` (comprehensive guide)
- **Test Connection**: `python scripts/test_connection.py`
- **MongoDB Atlas**: https://cloud.mongodb.com/
- **Beanie Docs**: https://beanie-odm.dev/

---

**Note:** Alembic is for SQL databases (PostgreSQL, MySQL). MongoDB doesn't need traditional migrations since it's schema-less. Beanie handles schema evolution automatically through your Pydantic models! 🚀
