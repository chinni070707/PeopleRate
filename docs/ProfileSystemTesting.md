# Profile System Testing Guide

## 🧪 Testing the New Profile System

### **Profile Features to Test:**

#### **1. Login and Profile Display**
1. **Navigate to**: http://127.0.0.1:8000
2. **Expected**: Top right shows "Write a Review" button (logged out state)
3. **Click**: "Write a Review" → redirects to `/auth`
4. **Login with existing account**:
   - Email: `john.reviewer@email.com`
   - Password: `password123`
5. **Expected**: Automatic redirect to homepage with profile button visible

#### **2. Profile Button and Dropdown**
1. **After login**: Top right should show profile button with:
   - Default avatar image
   - Username (e.g., "@TechReviewer2024")
   - Dropdown arrow
2. **Click profile button**: Dropdown menu should appear with:
   - Profile photo and user info header
   - "📷 Change Photo" option
   - "👤 View Profile" option  
   - "⭐ My Reviews" option
   - "⚙️ Settings" option
   - "🚪 Log Out" option

#### **3. Photo Upload Feature**
1. **Click**: "📷 Change Photo"
2. **Expected**: Modal popup with photo upload interface
3. **Test Upload**:
   - Click "Select Photo"
   - Choose any image file
   - Preview should appear
   - Click "Update Photo"
   - Profile photo should update in both button and dropdown

#### **4. Profile Menu Actions**
1. **View Profile**: Click → shows "coming soon" notification
2. **My Reviews**: Click → shows "coming soon" notification  
3. **Settings**: Click → shows "coming soon" notification
4. **Log Out**: Click → should log out and show "Write a Review" button again

#### **5. Mobile Responsiveness**
1. **Resize browser** to mobile width (400px)
2. **Expected**: 
   - Profile button adapts to smaller size
   - Username text disappears on small screens
   - Dropdown menu adjusts position
   - Modal becomes full-width

#### **6. Authentication Flow**
1. **Test Registration**:
   - Go to `/auth`
   - Click "Sign up here"
   - Fill form with new email and username
   - Should redirect to homepage with profile shown
2. **Test Logout/Login**:
   - Log out from profile menu
   - Refresh page → should remain logged out
   - Log back in → should remember profile state

### **🎯 Expected User Experience:**

#### **Logged Out State:**
- Navigation shows "Write a Review" button
- Clicking leads to authentication page

#### **Logged In State:**
- Navigation shows profile button with user photo and username
- Profile dropdown provides access to account management
- Smooth transitions and professional styling
- Photo upload works with preview functionality

#### **Visual Design:**
- TrustPilot green color scheme (#00b67a)
- Professional dropdown styling with shadows
- Smooth hover effects and transitions
- Default avatar for users without photos
- Success/error notifications for actions

### **🔧 Troubleshooting:**

#### **If Profile Not Showing:**
1. Check browser console for JavaScript errors
2. Verify token is stored: `localStorage.getItem('token')`
3. Check network tab for failed API calls
4. Try hard refresh (Ctrl+F5)

#### **If Photo Upload Not Working:**
1. Currently stores photos in localStorage (development mode)
2. Check browser storage limits
3. Try smaller image files
4. Check browser console for errors

#### **If Logout Not Working:**
1. Should clear localStorage tokens
2. Should redirect to logged-out state
3. Check browser developer tools → Application → Local Storage

### **🎉 Success Criteria:**
- ✅ Profile button appears when logged in
- ✅ Dropdown menu functions correctly
- ✅ Photo upload modal works
- ✅ Profile photo updates in real-time
- ✅ Logout clears session properly
- ✅ Mobile responsive design works
- ✅ Authentication flow is seamless
- ✅ Visual design matches TrustPilot style

---

*Test completed successfully when all features work as described above.*