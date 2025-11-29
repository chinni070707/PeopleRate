# Admin Dashboard Testing Guide

## 🎯 Quick Test: Admin Dashboard

### Step 1: Login as Admin
1. Go to http://localhost:8000/auth
2. Login with admin credentials:
   - **Username**: `TechReviewer2024` or `ProjectManager_Pro`
   - **Password**: `password123` (default from sample data)

### Step 2: Access Admin Dashboard
1. Go to http://localhost:8000/admin
2. You should see:
   - **Statistics cards**: Users, Persons, Reviews counts
   - **Three tabs**: Flagged Reviews, Recent Activity, User Management
   - **Modern UI**: Gradient header, responsive design

### Step 3: Test Content Moderation Flow

#### 3A. Flag a Review (as regular user)
1. Logout and login as regular user (or open incognito window)
2. Visit any person profile (e.g., http://localhost:8000/person/{person_id})
3. Find a review and click "🚩 Flag" button
4. Select reason: spam, harassment, false_info, inappropriate, or other
5. Add optional description
6. Submit flag

#### 3B. Moderate Flagged Content (as admin)
1. Login as admin: `TechReviewer2024` / `password123`
2. Go to http://localhost:8000/admin
3. Click "Flagged Reviews" tab
4. You should see the flagged review with:
   - Reporter username
   - Review content
   - Reason for flag
   - Action buttons: Approve, Reject, Dismiss
5. Test actions:
   - **Approve**: Clears flags, marks review as verified
   - **Reject**: Removes review permanently
   - **Dismiss**: Dismisses flag, keeps review

### Step 4: Check Recent Activity
1. In admin dashboard, click "Recent Activity" tab
2. See last 20 reviews across platform
3. Each review shows:
   - Person name
   - Reviewer username
   - Rating (1-5 stars)
   - Comment preview
   - Timestamp

### Step 5: View User Management
1. Click "User Management" tab
2. See top 10 users by review count
3. Check leaderboard:
   - Username
   - Number of reviews
   - Reputation score

## 🧪 Expected Behaviors

### ✅ Working Features
- Admin can only access with specific usernames (TechReviewer2024, ProjectManager_Pro)
- Flag submission requires authentication
- Flag counter updates in real-time
- Moderation actions update database immediately
- Review stats recalculate on reject action
- Non-admin users get 403 error

### ⚠️ Known Limitations (MVP)
- Admin check is username-based (simple for MVP)
- Flagged content stored in-memory (resets on restart)
- No pagination (shows all results)
- No email notifications (will add later)

## 🎨 UI Features to Notice

### Design Elements
- **Gradient Header**: Green gradient with white text
- **Statistics Cards**: Large numbers with icons
- **Tab Navigation**: Smooth switching between sections
- **Action Buttons**: Color-coded (green=approve, red=reject, gray=dismiss)
- **Hover Effects**: Buttons lift on hover with shadows
- **Responsive Grid**: Adapts to screen size

### Accessibility
- Semantic HTML structure
- Clear button labels
- Readable color contrast
- Keyboard navigation support

## 🚀 Social Sharing Test

### Test Share Buttons
1. Visit any person profile
2. Scroll to rating section
3. Find "Share:" buttons (Twitter, LinkedIn, Facebook)
4. Click each button:
   - **Twitter**: Opens popup with pre-filled tweet
   - **LinkedIn**: Opens LinkedIn share dialog
   - **Facebook**: Opens Facebook share dialog
5. Verify URL is included in share text

## 🔗 Error Pages Test

### Test 404 Page
1. Visit http://localhost:8000/nonexistent
2. Should see custom 404 page with:
   - Large "404" in green
   - Search icon emoji
   - "Page Not Found" message
   - Buttons: "Go to Homepage" and "Search People"

### Test 500 Page (Manual)
1. 500 page will show if server error occurs
2. Has red "500" text and warning icon
3. Buttons: "Go to Homepage" and "Try Again"

## 📝 Testing Checklist

- [ ] Admin login works
- [ ] Admin dashboard loads at /admin
- [ ] Statistics show correct counts
- [ ] Can switch between tabs smoothly
- [ ] Can flag a review as regular user
- [ ] Flagged review appears in admin dashboard
- [ ] "Approve" button works (clears flags)
- [ ] "Reject" button works (removes review)
- [ ] "Dismiss" button works (clears flag only)
- [ ] Recent activity shows last 20 reviews
- [ ] User management shows top 10 users
- [ ] Social share buttons open popups
- [ ] Share URLs include current page
- [ ] 404 page shows on bad URL
- [ ] Footer has Terms and Privacy links
- [ ] Non-admin users can't access /admin

## 🐛 If Something Doesn't Work

### Server Not Running
```powershell
# Restart server
uvicorn main:app --reload
```

### No Reviews to Flag
```powershell
# Generate sample data
.\venv\Scripts\python.exe scripts\generate_50_users.py
```

### Admin Access Denied
- Verify username is exactly: `TechReviewer2024` (case-sensitive)
- Or use: `ProjectManager_Pro`

### Flagged Content Not Showing
- Flags are in-memory, lost on server restart
- Flag a fresh review after server starts

## 📊 Success Metrics

### Admin Dashboard
- ✅ Loads in < 2 seconds
- ✅ All tabs clickable and functional
- ✅ Statistics accurate
- ✅ Actions take effect immediately

### Content Moderation
- ✅ Flag submission succeeds
- ✅ Flagged content appears in dashboard
- ✅ Moderation actions work correctly
- ✅ Counts update after actions

### User Experience
- ✅ UI is responsive and modern
- ✅ Buttons have clear hover effects
- ✅ Error messages are helpful
- ✅ Navigation is intuitive

---

**Ready to Test!** Server is running at http://localhost:8000
