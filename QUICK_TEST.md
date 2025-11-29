# Quick Manual Test Checklist

## ✅ Test These Features Now:

### 1. Homepage (http://localhost:8000)
- [ ] Page loads
- [ ] Search box visible
- [ ] Navigation works
- [ ] Footer has Terms/Privacy links

### 2. 404 Page (http://localhost:8000/test404)
- [ ] Custom 404 page shows
- [ ] Has green "404" text
- [ ] "Go to Homepage" button works

### 3. Search (http://localhost:8000)
- [ ] Type "John" in search
- [ ] Press Enter or click Search
- [ ] Results appear

### 4. Person Profile
- [ ] Click any person from search results
- [ ] Profile loads with rating
- [ ] **NEW**: Social share buttons visible (Twitter, LinkedIn, Facebook)
- [ ] Click share button - popup opens

### 5. Admin Dashboard (http://localhost:8000/admin)
- [ ] First login at http://localhost:8000/auth
  - Username: `TechReviewer2024`
  - Password: `password123`
- [ ] Go to http://localhost:8000/admin
- [ ] See statistics (Users, Persons, Reviews)
- [ ] Three tabs work: Flagged Reviews, Recent Activity, User Management

### 6. Flag & Moderate (Full Flow)
- [ ] Login as regular user
- [ ] Go to any person profile
- [ ] Click "🚩 Flag" on a review
- [ ] Select reason, submit
- [ ] Logout, login as admin (TechReviewer2024)
- [ ] Go to /admin
- [ ] See flagged review in "Flagged Reviews" tab
- [ ] Click "Approve", "Reject", or "Dismiss"
- [ ] Action completes successfully

---

## 🐛 If Issues Found:

**Server not responding:**
```powershell
# Restart server
.\venv\Scripts\python.exe -m uvicorn main:app --reload
```

**Can't login:**
- Check username is exactly: `TechReviewer2024` (case-sensitive)
- Password: `password123`

**404 not showing custom page:**
- Visit: http://localhost:8000/nonexistent
- Should see custom green 404 design

---

## 📊 Quick Results:
Mark ✅ for pass, ❌ for fail:

- Homepage: ___
- 404 Page: ___
- Search: ___
- Person Profile: ___
- Social Share: ___
- Admin Login: ___
- Admin Dashboard: ___
- Flag Review: ___
- Moderate Content: ___

**Overall: ___/9 working**
