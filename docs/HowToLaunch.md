# How to Launch PeopleRate Application

## Overview
This guide provides step-by-step instructions for launching the PeopleRate application, a TrustPilot-inspired people review platform built with FastAPI, Python, and modern web technologies.

---

## 🚀 Quick Start (TL;DR)

```bash
# 1. Navigate to project directory
cd "c:\Users\mahchi01\OneDrive - Cadence Design Systems Inc\Documents\PeopleRate"

# 2. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 3. Launch the application
uvicorn main:app --host 127.0.0.1 --port 8000

# 4. Open browser to http://127.0.0.1:8000
```

---

## 📋 Prerequisites

### **System Requirements:**
- **Operating System**: Windows 10/11
- **Python**: 3.8+ (with pip)
- **PowerShell**: For running commands
- **Internet Browser**: Chrome, Firefox, Edge, or Safari

### **Required Dependencies:**
The following packages are already installed in the virtual environment:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `pydantic` - Data validation
- `PyJWT` - JWT token authentication
- `bcrypt` - Password hashing
- `jinja2` - Template engine

---

## 🛠️ Step-by-Step Launch Instructions

### **Step 1: Open PowerShell**
1. Press `Win + R`
2. Type `powershell` and press Enter
3. Navigate to the project directory:
   ```powershell
   cd "c:\Users\mahchi01\OneDrive - Cadence Design Systems Inc\Documents\PeopleRate"
   ```

### **Step 2: Activate Virtual Environment**
```powershell
.\venv\Scripts\Activate.ps1
```

**Expected Output:**
```
(venv) PS C:\Users\mahchi01\OneDrive - Cadence Design Systems Inc\Documents\PeopleRate>
```

**Note:** The `(venv)` prefix indicates the virtual environment is active.

### **Step 3: Launch the Application**
```powershell
uvicorn main:app --host 127.0.0.1 --port 8000
```

**Expected Output:**
```
INFO:     Started server process [XXXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

### **Step 4: Verify Server is Running**
Open a new PowerShell window and run:
```powershell
netstat -an | findstr :8000
```

**Expected Output:**
```
TCP    127.0.0.1:8000        0.0.0.0:0              LISTENING
```

### **Step 5: Access the Application**
Open your web browser and navigate to:
- **Main Application**: http://127.0.0.1:8000
- **Authentication Page**: http://127.0.0.1:8000/auth
- **API Documentation**: http://127.0.0.1:8000/docs

---

## 🎯 Application Features to Test

### **🏠 Homepage (http://127.0.0.1:8000)**
- **Search Functionality**: Try searching for:
  - `"Microsoft"` - Find Microsoft employees
  - `"Seattle"` - Find people in Seattle
  - `"Technology"` - Browse technology professionals
  - `"alice.johnson@microsoft.com"` - Email search
  - `"+1-555-0123"` - Phone number search

- **Category Browsing**: Click on category tags:
  - 🖥️ Technology
  - 🏥 Healthcare  
  - 💰 Finance
  - 🎓 Education

- **Sample Data**: View 6 pre-loaded professional profiles:
  - Alice Johnson (Microsoft - Software Engineer)
  - Robert Chen (Google - Product Manager)
  - Emily Rodriguez (Apple - UX Design Director)
  - David Kim (Amazon - Data Scientist)
  - Sarah Thompson (McKinsey - Management Consultant)
  - Dr. Michael Brown (Johns Hopkins - Cardiologist)

### **🔐 Authentication (http://127.0.0.1:8000/auth)**
- **Test Login**: Use existing accounts:
  - Email: `john.reviewer@email.com`, Password: `password123`
  - Email: `sarah.manager@email.com`, Password: `password123`
  - Email: `mike.colleague@email.com`, Password: `password123`

- **Register New Account**: Create your own username (e.g., `@YourUsername2024`)

- **Privacy Features**: Notice how only usernames appear on reviews, not real names

### **📚 API Documentation (http://127.0.0.1:8000/docs)**
- Interactive Swagger documentation
- Test API endpoints directly in browser
- View data models and response schemas

---

## 🔧 Troubleshooting

### **Common Issues and Solutions:**

#### **❌ Issue: "Port 8000 is already in use"**
**Solution:**
```powershell
# Kill existing processes on port 8000
taskkill /f /im python.exe

# Or use different port
uvicorn main:app --host 127.0.0.1 --port 8001
```

#### **❌ Issue: "Virtual environment not found"**
**Solution:**
```powershell
# Ensure you're in the correct directory
cd "c:\Users\mahchi01\OneDrive - Cadence Design Systems Inc\Documents\PeopleRate"

# Check if venv folder exists
ls venv
```

#### **❌ Issue: "Module not found errors"**
**Solution:**
```powershell
# Ensure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Reinstall dependencies if needed
pip install -r requirements.txt
```

#### **❌ Issue: "Cannot access application in browser"**
**Solutions:**
1. **Check server is running**: Look for "Uvicorn running on..." message
2. **Verify port**: Use `netstat -an | findstr :8000`
3. **Try different browsers**: Chrome, Firefox, Edge
4. **Check firewall**: Ensure localhost/127.0.0.1 is not blocked
5. **Clear browser cache**: Ctrl+F5 to force refresh

#### **❌ Issue: "Static files not loading (no CSS styling)"**
**Solution:**
```powershell
# Ensure static folder exists
ls static/css/trustpilot_style.css

# Restart server if files were recently modified
# Press Ctrl+C to stop, then restart with uvicorn command
```

---

## 🛑 Stopping the Application

### **Method 1: Keyboard Shortcut**
In the PowerShell window running the server, press:
```
Ctrl + C
```

### **Method 2: Force Kill (if unresponsive)**
```powershell
taskkill /f /im python.exe
```

**Expected Output:**
```
INFO:     Shutting down
INFO:     Waiting for application shutdown.
INFO:     Application shutdown complete.
INFO:     Finished server process [XXXXX]
```

---

## 🚀 Alternative Launch Methods

### **Method 1: With Auto-Reload (Development)**
```powershell
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```
**Benefits**: Automatically restarts server when code changes

### **Method 2: Public Access (Network)**
```powershell
uvicorn main:app --host 0.0.0.0 --port 8000
```
**Benefits**: Allows access from other devices on same network
**Access URLs**: 
- Local: http://127.0.0.1:8000
- Network: http://[YOUR_IP]:8000

### **Method 3: Custom Port**
```powershell
uvicorn main:app --host 127.0.0.1 --port 8080
```
**Access URL**: http://127.0.0.1:8080

---

## 📊 Application Architecture

### **File Structure:**
```
PeopleRate/
├── main.py                 # Main application file
├── templates/              # HTML templates
│   ├── index.html
│   └── auth.html
├── static/                 # Static assets
│   └── css/
│       └── style.css
├── venv/                   # Virtual environment
├── docs/                   # Documentation
└── requirements.txt        # Dependencies
```

### **Technology Stack:**
- **Backend**: FastAPI (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **Authentication**: JWT + BCrypt
- **Data Storage**: In-memory (for development)
- **Server**: Uvicorn ASGI

---

## 🔄 Development Workflow

### **Making Changes:**
1. **Edit Code**: Modify files in project directory
2. **Restart Server**: Press Ctrl+C, then re-run uvicorn command
3. **Test Changes**: Refresh browser (Ctrl+F5 for hard refresh)
4. **Check Logs**: Monitor PowerShell window for errors

### **Adding New Features:**
1. **Update main.py**: Add new API endpoints
2. **Update templates**: Modify HTML files in templates/
3. **Update styles**: Edit static/css/style.css
4. **Document Changes**: Update UpdateHistory.md

---

## 📞 Support and Resources

### **Documentation:**
- **UpdateHistory.md**: Complete change log
- **README.md**: Project overview
- **API Docs**: http://127.0.0.1:8000/docs (when running)

### **Sample Data for Testing:**
- **Users**: 3 registered users with credentials above
- **Persons**: 6 professional profiles across different industries
- **Reviews**: 7 detailed reviews with anonymous usernames
- **Search Terms**: "Microsoft", "Seattle", "Technology", email addresses, phone numbers

### **Key URLs (when running):**
- 🏠 **Homepage**: http://127.0.0.1:8000
- 🔐 **Auth**: http://127.0.0.1:8000/auth  
- 📚 **API Docs**: http://127.0.0.1:8000/docs
- 🔍 **Search API**: http://127.0.0.1:8000/api/persons/search?q=Microsoft
- 📝 **Reviews API**: http://127.0.0.1:8000/api/reviews

---

## ✅ Success Checklist

After following this guide, you should have:
- [ ] PowerShell with virtual environment activated
- [ ] Server running with "Uvicorn running on..." message
- [ ] Port 8000 listening (verified with netstat)
- [ ] Homepage loading with TrustPilot design
- [ ] CSS styling applied correctly
- [ ] Search functionality working
- [ ] Sample data displaying (6 persons, 7 reviews)
- [ ] Authentication page accessible
- [ ] API documentation accessible

**🎉 If all items are checked, your PeopleRate application is successfully running!**

---

*Last Updated: November 6, 2025*  
*Version: 2.1.1*