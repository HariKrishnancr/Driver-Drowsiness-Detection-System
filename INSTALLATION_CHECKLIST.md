# ✅ Installation & Setup Verification Checklist

## 🎯 Pre-Installation Check

### System Requirements
- [ ] Python 3.6 or higher installed
- [ ] Webcam/camera available
- [ ] Modern web browser (Chrome, Firefox, Edge)
- [ ] Internet connection (for initial package downloads)

---

## 📦 Step-by-Step Installation Verification

### Step 1: Check Python Installation
```bash
python --version
```
**Expected Output:** `Python 3.x.x` (3.6 or higher)

✅ **Status:** _______

---

### Step 2: Verify Project Files
Check that all required files exist:

```
Drowsiness_Detection-master/
├── [✓] app.py                          # Main web app
├── [✓] Drowsiness_Detection.py         # Original script
├── [✓] requirements.txt                # Dependencies
├── [✓] run_web_app.bat                 # Launcher
├── [✓] templates/                      # HTML folder
│   ├── [✓] login.html
│   ├── [✓] register.html
│   └── [✓] detect.html
├── [✓] models/                         # Models folder
└── [✓] DOCUMENTATION FILES
    ├── [✓] QUICK_START.md
    ├── [✓] WEB_APPLICATION.md
    ├── [✓] PROJECT_SUMMARY.md
    ├── [✓] DEMO_GUIDE.md
    └── [✓] INSTALLATION_CHECKLIST.md   # This file
```

✅ **Status:** _______

---

### Step 3: Install Dependencies

#### Option A: Install All at Once
```bash
pip install -r requirements.txt
```

#### Option B: Install Individually
```bash
pip install opencv-python
pip install imutils
pip install dlib        # Optional but recommended
pip install scipy
pip install flask
```

✅ **Status:** _______

---

### Step 4: Verify Package Installation

Run these commands to verify each package:

```bash
python -c "import cv2; print('OpenCV:', cv2.__version__)"
python -c "import flask; print('Flask:', flask.__version__)"
python -c "import scipy; print('Scipy:', scipy.__version__)"
python -c "import imutils; print('Imutils: OK')"
```

**Expected Output:**
```
OpenCV: 4.x.x
Flask: 3.x.x
Scipy: 1.x.x
Imutils: OK
```

✅ **Status:** _______

---

### Step 5: Download Dlib Model (Optional but Recommended)

1. Download shape predictor from:
   ```
   https://sourceforge.net/projects/dclib/files/dlib/v19.10/shape_predictor_68_face_landmarks.dat.bz2
   ```

2. Extract the `.dat` file from the `.bz2` archive

3. Place it in the `models` folder:
   ```
   models/shape_predictor_68_face_landmarks.dat
   ```

✅ **Status:** _______ (Optional)

---

### Step 6: Test Database Creation

Run the application once to trigger database creation:

```bash
python app.py
```

**Look for this message:**
```
Database initialized successfully
```

Then check if `users.db` file was created in the project folder.

✅ **Status:** _______

---

### Step 7: Verify Web Server Starts

After running `python app.py`, look for:

```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.1.XXX:5000
```

✅ **Status:** _______

---

### Step 8: Test Web Interface

Open browser and navigate to: `http://127.0.0.1:5000`

**Verify:**
- [ ] Login page loads
- [ ] Purple gradient background appears
- [ ] Username and password fields visible
- [ ] "Register here" link visible
- [ ] No error messages

✅ **Status:** _______

---

### Step 9: Test User Registration

1. Click "Register here"
2. Fill in registration form:
   - Username: `testuser`
   - Password: `test123`
   - Confirm Password: `test123`
3. Click "Register"

**Expected Result:** Redirected to login page

✅ **Status:** _______

---

### Step 10: Test User Login

1. Enter credentials:
   - Username: `testuser`
   - Password: `test123`
2. Click "Login"

**Expected Result:** Redirected to detection page

✅ **Status:** _______

---

### Step 11: Test Camera Access

On the detection page:

1. Browser will ask for camera permission
2. Click "Allow"
3. Wait for video feed to appear

**Verify:**
- [ ] Video stream appears
- [ ] Can see your webcam feed
- [ ] Green face/eye detection boxes appear (when face is visible)

✅ **Status:** _______

---

### Step 12: Test Drowsiness Detection

1. Position your face in front of camera
2. Keep eyes open normally (should see green contours)
3. Close your eyes for 2-3 seconds
4. Watch for "ALERT!" message

**Verify:**
- [ ] Eye tracking works (green contours)
- [ ] Counter increases when eyes closed
- [ ] Red "ALERT!" appears after ~15 frames
- [ ] Alert disappears when eyes open

✅ **Status:** _______

---

### Step 13: Test Logout

1. Click "Logout" button in top-right
2. Should redirect to login page
3. Try going back to detection page (should require login again)

✅ **Status:** _______

---

## 🔧 Troubleshooting Common Issues

### Issue 1: "ModuleNotFoundError: No module named 'flask'"

**Solution:**
```bash
pip install flask
```

---

### Issue 2: "Port 5000 already in use"

**Solution 1:** Find and close the program using port 5000
```bash
netstat -ano | findstr :5000
```

**Solution 2:** Change port in `app.py`:
```python
# Line 209 in app.py
app.run(debug=True, host='0.0.0.0', port=5001)  # Changed to 5001
```

---

### Issue 3: Camera not working

**Possible Causes:**
- Another application is using the camera
- Browser blocked camera permissions
- Camera driver issues

**Solutions:**
1. Close other apps using camera (Zoom, Skype, etc.)
2. In browser settings, allow camera access
3. Update camera drivers
4. Try a different USB port

---

### Issue 4: "No module named 'cv2'"

**Solution:**
```bash
pip install opencv-python
```

If that fails:
```bash
python -m pip install opencv-python
```

---

### Issue 5: Dlib installation fails

**Windows Solution:**
1. Download pre-built wheel from:
   ```
   https://pypi.org/project/dlib/#files
   ```
2. Choose the correct version for your Python
3. Install with:
   ```bash
   pip install path\to\downloaded\wheel.whl
   ```

**Alternative:** Use OpenCV fallback (dlib is optional)

---

### Issue 6: Database errors

**Reset Database:**
```bash
# Delete existing database
del users.db

# Restart application
python app.py
```

---

### Issue 7: Templates not found

**Verify folder structure:**
```
project_folder/
├── app.py
└── templates/          ← Must be named exactly this
    ├── login.html
    ├── register.html
    └── detect.html
```

**Check case sensitivity:** "templates" not "Templates"

---

## 📊 Final Verification Summary

### Installation Complete When:

✅ All Python packages installed  
✅ Web server starts successfully  
✅ Login page loads in browser  
✅ User registration works  
✅ User login works  
✅ Camera feed displays  
✅ Face/eye detection active  
✅ Drowsiness alerts trigger  
✅ Logout functions correctly  

---

## 🎯 Performance Benchmarks

### Expected Performance:

| Metric | Target | Acceptable Range |
|--------|--------|------------------|
| Page Load Time | < 1s | < 3s |
| Video Latency | < 200ms | < 500ms |
| Face Detection | Instant | < 100ms |
| Alert Trigger | ~0.5s | < 1s |
| Database Query | < 10ms | < 50ms |

---

## 🔐 Security Verification

### Basic Security Checks:

✅ SQL injection prevention (parameterized queries)  
✅ Session-based authentication  
✅ Password confirmation on registration  
✅ Unique username constraint  
✅ Session cleared on logout  

⚠️ **Note:** For production, add password hashing and HTTPS

---

## 📝 Installation Log Template

```
Date: _______________
Installer: _______________

Step 1 - Python Version: _______________
Step 2 - Files Verified: ☐ Yes ☐ No
Step 3 - Dependencies Installed: ☐ Yes ☐ No
Step 4 - Packages Verified: ☐ Yes ☐ No
Step 5 - Dlib Model: ☐ Downloaded ☐ Skipped
Step 6 - Database Created: ☐ Yes ☐ No
Step 7 - Server Started: ☐ Yes ☐ No
Step 8 - Login Page: ☐ Works ☐ Issues
Step 9 - Registration: ☐ Works ☐ Issues
Step 10 - Login: ☐ Works ☐ Issues
Step 11 - Camera: ☐ Works ☐ Issues
Step 12 - Detection: ☐ Works ☐ Issues
Step 13 - Logout: ☐ Works ☐ Issues

Overall Status: ☐ SUCCESS ☐ PARTIAL ☐ FAILED

Notes:
_______________________________________
_______________________________________
_______________________________________
```

---

## 🎉 Success Confirmation

If all steps pass, you should see:

```
✅ Database initialized successfully
✅ Serving Flask app 'app'
✅ Running on http://127.0.0.1:5000
✅ All features operational
```

**Your web application is ready for use!** 🚀

---

## 📞 Next Steps After Installation

1. **Test thoroughly** using the test scenarios
2. **Read documentation:**
   - `QUICK_START.md` - Quick usage guide
   - `WEB_APPLICATION.md` - Detailed documentation
   - `DEMO_GUIDE.md` - Visual walkthrough
   - `PROJECT_SUMMARY.md` - Complete overview

3. **Create your user account** via registration
4. **Test the drowsiness detection** with good lighting
5. **Bookmark the URL:** http://127.0.0.1:5000

---

## 🆘 Still Having Issues?

If problems persist:

1. Check Python version compatibility (3.6+)
2. Verify all dependencies are installed
3. Review error messages carefully
4. Check browser console for JavaScript errors
5. Ensure camera permissions are granted
6. Try a different browser
7. Restart your computer
8. Reinstall problematic packages

---

**Installation Checklist Complete** ✅

Proceed to `QUICK_START.md` for usage instructions!
