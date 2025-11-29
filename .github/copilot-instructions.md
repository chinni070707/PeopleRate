# PeopleRate Development Instructions

This is a FastAPI-based people review platform similar to TrustPilot but for individuals.

## 🎯 CURRENT STATUS (Nov 28, 2025)
**Phase:** Autonomous completion for launch  
**Mode:** Agent completing project with full autonomy  
**Goal:** Make launch-ready and viral-worthy  
**Progress:** 75% complete (MVP), working on production-ready features

## Project Status
- [x] Project Structure Setup - FastAPI app with proper folder structure
- [x] Database Models - Pydantic + Beanie ODM models for MongoDB
- [x] Authentication System - JWT-based auth with bcrypt
- [x] API Endpoints - REST endpoints for core functionality
- [x] NLP System - Revolutionary 500+ line natural language processor
- [x] Multi-Platform Social - LinkedIn, Instagram, Facebook, Twitter, GitHub, Website
- [x] Search Engine - Smart threshold-based search (score >= 30)
- [x] Profile Photos - Client-side upload with validation
- [x] Frontend Templates - HTML/CSS/JS with Jinja2
- [x] Strategic Planning - Business model analysis, 12-week program timeline
- [x] Completeness Analysis - 50+ page detailed analysis
- [x] MongoDB Infrastructure - Beanie ODM, 6 models, migration scripts ready
- [x] Hybrid Database Mode - Works in-memory OR MongoDB (configurable)

## 🚧 In Progress (Current Session)
- [ ] Content Moderation System - Profanity filter, flagging, legal protection
- [ ] Legal Documents - ToS, Privacy Policy, GDPR compliance
- [ ] Email Verification - File-based mock for MVP, SendGrid-ready
- [ ] Security Hardening - Rate limiting, secrets, CORS, headers
- [ ] Profile Claiming - Viral feature for user engagement
- [ ] Social Sharing - Twitter/LinkedIn/Facebook share buttons
- [ ] Verification Badges - Email, LinkedIn, company verified
- [ ] Error Pages & Polish - 404, 500, loading states, UX improvements
- [ ] Deployment Prep - Render.com config, production checklist

## Tech Stack
- **Backend:** FastAPI (Python) with async/await
- **Database:** MongoDB Atlas (Beanie ODM) + In-memory fallback
- **Authentication:** JWT + bcrypt password hashing
- **NLP:** Custom natural language processor (500+ lines)
- **Frontend:** HTML/CSS/JS (MVP) with Jinja2 templates
- **Deployment:** Render.com (target platform)
- **Environment:** Python 3.8+, Virtual environment (venv)

## 📊 Key Features
1. **Revolutionary NLP Search** - Natural language person creation and search
2. **Multi-Platform Social** - 6 social media platforms supported
3. **Anonymous Reviews** - Privacy-first with public usernames
4. **Smart Search** - Threshold-based relevance (score >= 30)
5. **Profile Photos** - Upload and preview with validation
6. **Balanced Model** - Positive + negative reviews (18x more profitable than negative-only)

## 🗄️ Database Architecture
**Current Mode:** Hybrid (in-memory with MongoDB-ready)

**Collections (6 Beanie Models):**
- `users` - User accounts, authentication, reputation
- `persons` - Person profiles being reviewed
- `reviews` - Review content with ratings
- `notifications` - User notifications
- `subscriptions` - Premium tier management (future)
- `flagged_content` - Content moderation queue

**Migration Status:**
- ✅ Models defined with indexes
- ✅ Connection utilities ready
- ✅ Migration scripts created
- ⏸️ MongoDB Atlas credentials needed (optional for MVP)
- ✅ In-memory mode works fully for testing

## 🔐 Security Status
**Current:** Development mode (needs hardening)
**Planned:**
- Rate limiting (slowapi)
- JWT_SECRET in environment
- CORS restrictions (remove wildcard)
- Security headers
- Input sanitization
- Profanity filtering

## 🚀 Deployment Strategy
**Target:** Render.com (free tier)
**Status:** Ready to deploy after feature completion

**Requirements:**
1. Render.com account (user needs to create)
2. Environment variables configured
3. Production security enabled
4. Legal docs in place
5. Content moderation active

## 📁 Project Structure
```
PeopleRate/
├── app/
│   ├── models/
│   │   └── mongodb_models.py      # 6 Beanie ODM models
│   └── utils/
│       └── database.py             # MongoDB connection
├── scripts/
│   ├── init_sample_data.py        # Sample data initialization
│   ├── migrate_to_mongodb.py      # Migration script
│   └── test_connection.py         # MongoDB connection test
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── templates/
│   ├── index.html                 # Homepage
│   ├── search.html                # Search results
│   ├── person_detail.html         # Profile page
│   ├── profile.html               # User profile (edit)
│   ├── my-reviews.html            # User's reviews
│   ├── register.html
│   └── login.html
├── main.py                        # FastAPI application (1125 lines)
├── nlp_processor.py               # NLP engine (500+ lines)
├── requirements.txt
├── .env                           # Environment variables
├── COMPLETENESS_ANALYSIS.md       # 50+ page analysis
├── BLOCKERS_AND_DECISIONS.md      # Current blockers
├── programManager.md              # 12-week timeline
└── MONGODB_ATLAS_SETUP.md         # MongoDB setup guide
```

## 🔄 Sample Data
**In-Memory Mode (Current):**
- 3 users (TechReviewer2024, ProjectManager_Pro, DataScience_Mike)
- 10 persons (Alice Johnson, Robert Chen, Emily Rodriguez, 2x Sasikala, etc.)
- 7 reviews with detailed ratings

**MongoDB Mode (When enabled):**
- Automatic initialization from scripts/init_sample_data.py
- Same data structure
- Persistent across restarts

## 🎨 Design Philosophy
1. **Privacy-First:** Anonymous reviews with public usernames
2. **Balanced Reviews:** Positive + negative (not negative-only like ScamAlert)
3. **NLP-Powered:** Revolutionary natural language person creation
4. **Multi-Platform:** 6 social media platforms
5. **Viral-Worthy:** Profile claiming, sharing, badges
6. **Launch Fast:** MVP first, iterate based on feedback

## 💡 Business Model (Analyzed)
- **Balanced reviews:** 18x more profitable than negative-only
- **Market:** Professional review platform (TrustPilot for people)
- **Revenue (Future):** Freemium subscriptions, premium features
- **Current Focus:** User growth and viral adoption (monetization later)

## 🐛 Known Issues & Solutions
1. ~~Search returning unrelated users~~ ✅ Fixed (score >= 30 threshold)
2. ~~LinkedIn-only limitation~~ ✅ Fixed (6 platforms now)
3. ~~Profile photo not in edit form~~ ✅ Fixed (integrated)
4. Data persistence: Optional MongoDB (in-memory works for MVP)

## 🔧 Development Commands
```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run server (ALWAYS use --reload and run in BACKGROUND)
# This keeps the chat available while server runs
.\venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000 &

# Or in PowerShell (background mode):
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000"

# IMPORTANT: Always start server in background so user can continue chatting!
# Never block the terminal with foreground server processes during development

# Test MongoDB connection (if configured)
python scripts/test_connection.py

# Migrate to MongoDB (if configured)
python scripts/migrate_to_mongodb.py
```

## 📝 Environment Variables (.env)
```bash
# MongoDB (Optional - works without it)
MONGODB_URL=mongodb+srv://USERNAME:PASSWORD@CLUSTER_URL/
DATABASE_NAME=peopleRate_db

# JWT Security
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=development  # or production
```

## 🎯 Success Metrics
- **MVP Completion:** 75%
- **Production Ready:** 30% → Working on remaining 70%
- **Lines of Code:** 2000+ (main.py: 1125, nlp: 500+)
- **Features:** 90% of planned features implemented
- **Documentation:** Comprehensive (5+ detailed docs)

## 🚦 Deployment Checklist
- [ ] Content moderation active
- [ ] Legal documents (ToS, Privacy)
- [ ] Security hardened (rate limit, CORS, headers)
- [ ] Error handling (404, 500 pages)
- [ ] Email verification (mock or real)
- [ ] Render.com account created
- [ ] Environment variables set
- [ ] Domain configured (optional)
- [ ] Analytics tracking (Google Analytics)

## 🤝 Contributing Guidelines
**Current Mode:** Single autonomous agent completing project  
**Review Required:** Legal documents (ToS, Privacy) should be lawyer-reviewed before scale  
**Testing:** Test locally before deploying to production

## 📞 Support & Blockers
See `BLOCKERS_AND_DECISIONS.md` for:
- Current blockers requiring user input
- Decisions made by autonomous agent
- Workarounds implemented
- Launch readiness status