# 🌐 How to Access Your Drowsiness Detection Website

## ✅ TWO WAYS TO ACCESS - Choose What Works Best for You!

---

## 🎯 **METHOD 1: Direct Flask Access (RECOMMENDED)**

### This is the EASIEST and MOST RELIABLE method!

#### Step 1: Start the Application
**Option A:** Double-click `START_HERE.bat`  
**Option B:** Run manually:
```bash
cd c:\wamp64\www\Drowsiness_Detection-master
python app.py
```

#### Step 2: Access in Browser
Your browser will open automatically, or manually go to:
```
http://localhost:5000
```

✅ **Advantages:**
- No configuration needed
- Works immediately
- Fastest performance
- Full Flask features
- Easy troubleshooting

---

## 📁 **METHOD 2: Via WAMP Folder Name**

If you want to access it as `http://localhost/Drowsiness_Detection-master`:

### Option A: Using index.html Redirect (Simple)

1. Make sure Flask is running (`python app.py`)
2. In browser, go to:
   ```
   http://localhost/Drowsiness_Detection-master/index.html
   ```
3. It will automatically redirect to the Flask app

### Option B: Apache Proxy Setup (Advanced)

Requires WAMP configuration changes - see `WAMP_SETUP.md` for detailed instructions.

---

## 🚀 **QUICK START - Just Do This!**

### Easiest Way:
1. **Double-click:** [`START_HERE.bat`](file:///c:/wamp64/www/Drowsiness_Detection-master/START_HERE.bat)
2. **Wait** for browser to open automatically
3. **Register** a new account
4. **Login** and start detecting!

That's it! 🎉

---

## 📋 **What Each Method Does**

### METHOD 1: Flask Server (Port 5000)
```
User clicks START_HERE.bat
    ↓
Flask server starts on port 5000
    ↓
Browser opens: http://localhost:5000
    ↓
Login page appears
    ↓
Full functionality available
```

**URL:** `http://localhost:5000`  
**Port:** 5000  
**Requirements:** Python + Flask  
**Complexity:** ⭐ Very Easy  

---

### METHOD 2: WAMP Folder Access
```
User visits: http://localhost/Drowsiness_Detection-master
    ↓
index.html loads
    ↓
Auto-redirects to: http://localhost:5000
    ↓
Same Flask app as Method 1
```

**URL:** `http://localhost/Drowsiness_Detection-master`  
**Port:** 80 (Apache) → 5000 (Flask)  
**Requirements:** WAMP running + Flask running  
**Complexity:** ⭐⭐ Medium (needs redirect)  

---

## 🔍 **Understanding the Setup**

### Why Two Methods?

Your application is built with **Python Flask**, which has its own web server.

**Method 1** uses Flask's server directly.  
**Method 2** uses WAMP's Apache as a "front door" that redirects to Flask.

### Architecture Diagram:

```
┌──────────────────────────────────────────────┐
│              METHOD 1 (Direct)               │
│                                              │
│  Browser → http://localhost:5000 → Flask    │
│                                    ↓         │
│                              Login Page      │
│                                    ↓         │
│                              Detection       │
└──────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐
│           METHOD 2 (Via WAMP Folder)         │
│                                              │
│  Browser → http://localhost/                 │
│            /Drowsiness_Detection-master      │
│                                    ↓         │
│          Apache (WAMP) serves index.html     │
│                                    ↓         │
│          Auto-redirect to port 5000          │
│                                    ↓         │
│                              Flask Server    │
│                                    ↓         │
│                              Login Page      │
└──────────────────────────────────────────────┘
```

---

## 💻 **Step-by-Step Tutorial**

### First Time Setup:

#### 1. Install Dependencies (One-time only)
```bash
pip install -r requirements.txt
```

Or just run `START_HERE.bat` - it does this automatically!

#### 2. Start the Server
```bash
python app.py
```

Look for this message:
```
 * Running on http://127.0.0.1:5000
Database initialized successfully
```

#### 3. Open Browser
Navigate to: `http://localhost:5000`

#### 4. Register New Account
- Click "Register here"
- Username: Choose any name
- Password: Create a password
- Confirm password
- Click "Register"

#### 5. Login
- Enter your username and password
- Click "Login"

#### 6. Start Detection
- Allow camera access when prompted
- Position face in front of camera
- System will track your eyes!

---

## 🎯 **Access URLs Summary**

| What You Type | Where It Goes | Port | Notes |
|---------------|---------------|------|-------|
| `http://localhost:5000` | Flask App | 5000 | ✅ Direct access |
| `http://127.0.0.1:5000` | Flask App | 5000 | Same as above |
| `http://localhost/Drowsiness_Detection-master/index.html` | Redirects to Flask | 80→5000 | Uses WAMP |
| `http://localhost/Drowsiness_Detection-master/` | Shows folder (if WAMP allows) | 80 | May show file list |

---

## 🛠️ **Troubleshooting**

### Problem: "Port 5000 already in use"

**Solution:**
```bash
# Find what's using port 5000
netstat -ano | findstr :5000

# Kill the process (replace PID with actual number)
taskkill /PID [number] /F

# Or use a different port
# Edit app.py line 211, change port=5000 to port=5001
```

---

### Problem: "Cannot access localhost:5000"

**Check:**
1. Is Flask running? Look for: `Running on http://127.0.0.1:5000`
2. Try `http://127.0.0.1:5000` instead of localhost
3. Check Windows Firewall settings
4. Make sure no antivirus is blocking

---

### Problem: Want to use ONLY `http://localhost/Drowsiness_Detection-master`

You have two options:

**Option 1:** Set up Apache proxy (see `WAMP_SETUP.md`)

**Option 2:** Change Flask to use port 80:
```python
# In app.py line 211:
app.run(debug=True, host='127.0.0.1', port=80)
```
⚠️ Requires running as Administrator!

---

### Problem: Browser doesn't open automatically

Manual steps:
1. Wait for terminal to show: `Running on http://127.0.0.1:5000`
2. Open browser manually
3. Type: `http://localhost:5000`

---

## 📊 **Comparison Table**

| Feature | Method 1 (Direct) | Method 2 (WAMP) |
|---------|------------------|-----------------|
| **Speed** | ⚡ Faster | Slightly slower (redirect) |
| **Setup** | ✅ Simple | Needs WAMP running |
| **Reliability** | ✅ Very reliable | Depends on WAMP |
| **URL** | `localhost:5000` | `localhost/FolderName` |
| **Port** | 5000 | 80 → 5000 |
| **Best For** | Development | Integration with WAMP |

---

## 🎓 **Technical Details**

### Files Created for Access:

1. **`app.py`** - Main Flask application (the actual website)
2. **`START_HERE.bat`** - One-click launcher with auto-browser
3. **`index.html`** - Redirect page for WAMP folder access
4. **`.htaccess`** - Apache rewrite rules (for advanced setup)
5. **`index.php`** - PHP entry point (for WAMP integration)

### Database Location:
```
c:\wamp64\www\Drowsiness_Detection-master\users.db
```

Created automatically on first run.

---

## 🏆 **Recommended Workflow**

### Daily Use:
```
1. Double-click START_HERE.bat
2. Browser opens automatically
3. Use the application
4. Close browser when done
5. Press Ctrl+C in terminal to stop server
```

### If You Forget to Close:
The server keeps running in the background. That's fine! Just access it again anytime.

---

## 📝 **Quick Reference Card**

```
╔══════════════════════════════════════════╗
║  Drowsiness Detection - Quick Access    ║
╠══════════════════════════════════════════╣
║  1. Run: START_HERE.bat                  ║
║  2. URL: http://localhost:5000           ║
║  3. Register → Login → Detect!           ║
║                                          ║
║  Alternative URL:                        ║
║  http://localhost/Drowsiness_            ║
║             Detection-master/index.html  ║
║                                          ║
║  To Stop: Ctrl+C in terminal             ║
╚══════════════════════════════════════════╝
```

---

## 🎉 **Success Checklist**

✅ Python installed  
✅ Dependencies installed (`pip install -r requirements.txt`)  
✅ Flask server starts without errors  
✅ Browser can access `http://localhost:5000`  
✅ Login page loads  
✅ Registration works  
✅ Login works  
✅ Camera detection works  

If all checkboxes are ✅, you're all set! 🚀

---

## 🆘 **Still Need Help?**

1. Check `QUICK_START.md` for basic usage
2. Check `WAMP_SETUP.md` for advanced WAMP configuration
3. Check `INSTALLATION_CHECKLIST.md` for verification steps
4. Look at terminal error messages
5. Make sure WAMP is running (green icon) if using Method 2

---

## 📞 **Common Questions**

### Q: Do I need WAMP running for Method 1?
**A:** No! Flask has its own server. WAMP is only needed for Method 2.

### Q: Can I access from other computers on my network?
**A:** Yes! Change line 211 in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```
Then others can access: `http://YOUR_IP:5000`

### Q: Is this production-ready?
**A:** For production, use Gunicorn/uWSGI behind Apache/Nginx. See deployment guides.

### Q: Can I change the port?
**A:** Yes! Edit `app.py` line 211, change `port=5000` to any available port.

---

**Your website is ready to use!** 🎊

Just run `START_HERE.bat` and enjoy your drowsiness detection system!
