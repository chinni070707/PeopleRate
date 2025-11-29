# MongoDB Atlas Setup Guide for PeopleRate

## 🎯 Step-by-Step Configuration

### Step 1: Get Your MongoDB Atlas Connection String

1. **Log in to MongoDB Atlas:** https://cloud.mongodb.com/
2. **Click "Connect"** on your cluster
3. **Choose "Connect your application"**
4. **Copy the connection string** - it looks like:
   ```
   mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```

### Step 2: Configure Your .env File

1. Open `.env` file in your project root
2. Replace the placeholder with your actual credentials:

```bash
# Before (placeholder):
MONGODB_URL=mongodb+srv://<username>:<password>@<cluster-url>/?retryWrites=true&w=majority

# After (your actual credentials):
MONGODB_URL=mongodb+srv://myusername:MySecurePassword123@cluster0.ab1cd.mongodb.net/?retryWrites=true&w=majority
```

**Important Notes:**
- Replace `<username>` with your MongoDB Atlas username
- Replace `<password>` with your MongoDB Atlas password (URL encode special characters!)
- Replace `<cluster-url>` with your actual cluster URL (e.g., `cluster0.ab1cd.mongodb.net`)
- Keep the database name: `DATABASE_NAME=peopleRate_db`

### Step 3: URL Encode Special Characters in Password

If your password contains special characters, you MUST URL encode them:

| Character | URL Encoded |
|-----------|-------------|
| `@` | `%40` |
| `:` | `%3A` |
| `/` | `%2F` |
| `?` | `%3F` |
| `#` | `%23` |
| `[` | `%5B` |
| `]` | `%5D` |
| `!` | `%21` |
| `$` | `%24` |
| `&` | `%26` |
| `'` | `%27` |
| `(` | `%28` |
| `)` | `%29` |
| `*` | `%2A` |
| `+` | `%2B` |
| `,` | `%2C` |
| `;` | `%3B` |
| `=` | `%3D` |

**Example:**
- Password: `MyP@ss:w0rd!`
- Encoded: `MyP%40ss%3Aw0rd%21`

### Step 4: Whitelist Your IP Address

1. In MongoDB Atlas, go to **Network Access**
2. Click **"Add IP Address"**
3. Choose one:
   - **"Add Current IP Address"** (recommended for development)
   - **"Allow Access from Anywhere"** (`0.0.0.0/0`) - less secure but convenient

### Step 5: Install New Dependencies

```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install updated requirements
pip install -r requirements.txt
```

This will install:
- `beanie` - MongoDB ODM (Object Document Mapper)
- All other existing dependencies

### Step 6: Test the Connection

Run this test script:

```bash
python scripts/test_connection.py
```

You should see:
```
✅ Successfully connected to MongoDB
✅ Beanie ODM initialized with database: peopleRate_db
📊 Collections: users, persons, reviews, notifications, subscriptions, flagged_content
```

### Step 7: Initialize Sample Data (Optional)

```bash
python scripts/migrate_to_mongodb.py
```

This will:
1. Connect to MongoDB Atlas
2. Create all collections with indexes
3. Import sample data (users, persons, reviews)

---

## 🔧 What Changed?

### New Structure

**Before (In-Memory):**
```python
DATABASE = {
    "users": {},
    "persons": {},
    "reviews": {}
}
```

**After (MongoDB with Beanie):**
```python
from app.models.mongodb_models import User, Person, Review

# Create user
user = User(email="test@email.com", username="testuser", ...)
await user.insert()

# Find user
user = await User.find_one(User.email == "test@email.com")

# Update user
user.reputation_score = 100
await user.save()
```

### Benefits of New System

1. **✅ Data Persistence** - No more data loss on restart
2. **✅ Type Safety** - Pydantic validation on all fields
3. **✅ Automatic Indexing** - Fast queries on name, company, city, etc.
4. **✅ Relationships** - Proper document references
5. **✅ Scalability** - Cloud-hosted, auto-scaling
6. **✅ Backup** - Automatic backups on MongoDB Atlas
7. **✅ Query Power** - Complex queries with MongoDB syntax

---

## 📊 Database Schema

### Collections Created:

1. **users** - User accounts with authentication
   - Indexes: email (unique), username (unique), created_at
   
2. **persons** - Person profiles being reviewed
   - Indexes: name, company, city, email, compound(name+company)
   
3. **reviews** - Reviews about persons
   - Indexes: person_id, reviewer_id, created_at, moderation_status
   
4. **notifications** - User notifications
   - Indexes: user_id, is_read, created_at
   
5. **subscriptions** - Premium subscriptions
   - Indexes: user_id (unique), stripe_customer_id, status
   
6. **flagged_content** - Moderation queue
   - Indexes: content_id, status, created_at

---

## 🚨 Troubleshooting

### Error: "pymongo.errors.ServerSelectionTimeoutError"

**Cause:** Can't connect to MongoDB Atlas

**Solutions:**
1. Check your internet connection
2. Verify IP address is whitelisted in MongoDB Atlas
3. Verify connection string is correct in `.env`
4. Check username/password are correct
5. Ensure password is URL encoded

### Error: "Authentication failed"

**Cause:** Wrong username or password

**Solutions:**
1. Verify credentials in MongoDB Atlas dashboard
2. Make sure you're using database user (not Atlas account)
3. URL encode special characters in password
4. Try creating a new database user with simple password

### Error: "MongoWriteConcernError: not master"

**Cause:** Replica set primary election

**Solutions:**
1. Wait 30 seconds and try again
2. Check MongoDB Atlas cluster status
3. Restart your application

### Error: "beanie.exceptions.CollectionWasNotInitialized"

**Cause:** Beanie not initialized before using models

**Solutions:**
1. Make sure `await connect_to_mongo()` is called on startup
2. Check that all models are listed in `init_beanie()`
3. Restart the application

---

## 🎯 Next Steps After Setup

1. ✅ **Test Connection** - Run test script
2. ✅ **Initialize Data** - Run migration script
3. ✅ **Start Server** - `uvicorn main:app --reload`
4. ✅ **Test API** - Visit http://localhost:8000/docs
5. ✅ **Verify Data** - Check MongoDB Atlas dashboard

---

## 💡 Pro Tips

### Development Best Practices:

1. **Use .env.local for local overrides:**
   ```bash
   # .env.local (git-ignored)
   MONGODB_URL=mongodb://localhost:27017
   ```

2. **Check database stats:**
   ```python
   from app.utils.database import get_database_stats
   stats = await get_database_stats()
   print(stats)  # {'users': 10, 'persons': 50, 'reviews': 100}
   ```

3. **Index Monitoring:**
   - MongoDB Atlas Dashboard → Database → Collections → Indexes
   - Check for slow queries
   - Add indexes as needed

4. **Backup Strategy:**
   - Enable automated backups in MongoDB Atlas
   - Download backups weekly during development
   - Test restore process

---

## 📚 Beanie ORM Quick Reference

### Basic Operations:

```python
# CREATE
user = User(email="test@email.com", username="testuser")
await user.insert()

# READ
user = await User.find_one(User.email == "test@email.com")
users = await User.find(User.is_active == True).to_list()

# UPDATE
user.reputation_score = 100
await user.save()

# DELETE
await user.delete()

# FIND WITH FILTERS
users = await User.find(
    User.reputation_score > 50,
    User.is_active == True
).sort(-User.created_at).limit(10).to_list()

# COUNT
count = await User.find(User.is_active == True).count()

# AGGREGATION
pipeline = [
    {"$match": {"is_active": True}},
    {"$group": {"_id": "$subscription_tier", "count": {"$sum": 1}}}
]
result = await User.aggregate(pipeline).to_list()
```

---

## ✅ Migration Checklist

- [ ] MongoDB Atlas account created
- [ ] Cluster created and running
- [ ] Database user created with password
- [ ] IP address whitelisted
- [ ] Connection string copied
- [ ] `.env` file updated with connection string
- [ ] Password URL encoded (if needed)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Connection tested successfully
- [ ] Sample data initialized
- [ ] Server starts without errors
- [ ] API endpoints working
- [ ] Data visible in MongoDB Atlas dashboard

---

## 🎉 Success!

Once all checklist items are complete, you have:
- ✅ Production-ready database (MongoDB Atlas)
- ✅ Data persistence (no more in-memory!)
- ✅ Type-safe models (Beanie + Pydantic)
- ✅ Automatic indexing (fast queries)
- ✅ Scalable infrastructure (cloud-hosted)

**You've completed Week 1, Task 1 of the program plan! 🚀**

Next steps: Email verification (Week 2) and Payment integration (Week 3)
