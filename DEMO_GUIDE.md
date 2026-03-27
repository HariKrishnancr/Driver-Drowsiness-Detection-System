# 🎬 Application Demo Guide

## Visual Walkthrough - How the Web App Works

### Step 1: Initial Access
```
User opens browser → http://127.0.0.1:5000
        ↓
    Redirects to Login Page
```

---

### Step 2: Login Page Interface

**What You'll See:**
```
┌─────────────────────────────────────────┐
│                                         │
│              😴                         │
│                                         │
│     Drowsiness Detection                │
│                                         │
│     Username: [________________]        │
│                                         │
│     Password: [________________]        │
│                                         │
│     [      Login      ]                 │
│                                         │
│     Don't have an account?              │
│     Register here                       │
│                                         │
└─────────────────────────────────────────┘
```

**Actions:**
- Enter username
- Enter password
- Click "Login" button

**If New User:**
- Click "Register here" link
- Fill registration form
- Return to login

---

### Step 3: Registration Page (First-Time Users)

**What You'll See:**
```
┌─────────────────────────────────────────┐
│                                         │
│              📝                         │
│                                         │
│           Register                      │
│                                         │
│     Username: [________________]        │
│                                         │
│     Password: [________________]        │
│                                         │
│     Confirm Password: [________]        │
│                                         │
│     [     Register     ]                │
│                                         │
│     Already have an account?            │
│     Login here                          │
│                                         │
└─────────────────────────────────────────┘
```

**Actions:**
1. Choose username (must be unique)
2. Create password
3. Confirm password (must match)
4. Click "Register"
5. Auto-redirect to login page

---

### Step 4: Successful Login → Detection Page

**What You'll See:**
```
┌──────────────────────────────────────────────────────┐
│ 😴 Drowsiness Detection    Welcome, [username] [Logout]│
├──────────────────────────────────────────────────────┤
│                                                      │
│  Live Detection Feed                                 │
│  ┌────────────────────────────────────────────┐     │
│  │                                            │     │
│  │         [LIVE CAMERA FEED HERE]            │     │
│  │                                            │     │
│  │     Your face appears in this box          │     │
│  │     Real-time eye tracking active          │     │
│  │                                            │     │
│  └────────────────────────────────────────────┘     │
│                                                      │
│  How It Works                                        │
│  This system uses computer vision to detect         │
│  drowsiness by monitoring your eye movements...     │
│                                                      │
│  ⚠️ Alert System:                                    │
│  When closed eyes detected for 15 frames with       │
│  EAR < 0.25, visual alert triggers                  │
│                                                      │
│  Features:                                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │👁️ Eye    │  │⚡ Real-  │  │🚨 Instant│          │
│  │Tracking  │  │time      │  │Alerts    │          │
│  └──────────┘  └──────────┘  └──────────┘          │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---

### Step 5: Drowsiness Detection in Action

#### Normal State (Alert):
```
┌─────────────────────────────────────┐
│                                     │
│      [Your Face - Eyes Open]        │
│                                     │
│      Green contours around eyes     │
│      EAR > 0.25                     │
│      Status: ✅ Normal              │
│                                     │
└─────────────────────────────────────┘
```

#### Drowsy State (ALERT!):
```
┌─────────────────────────────────────┐
│                                     │
│   ****************ALERT!****************  ← Red text
│                                     │
│      [Your Face - Eyes Closed]      │
│                                     │
│   ****************ALERT!****************  ← Red text
│                                     │
│      EAR < 0.25 for 15+ frames      │
│      Status: ⚠️ DROWSY              │
│                                     │
└─────────────────────────────────────┘
```

---

## 🎯 Real-Time Detection States

### State 1: No Face Detected
```
Message: "No face detected"
Display: Normal camera view
Action: Wait for user to position face
```

### State 2: Face Detected, Monitoring
```
Display: Green boxes around face and eyes
Status: Active monitoring
EAR Calculation: Running
Counter: flag = 0
```

### State 3: Eyes Closing (Potential Drowsiness)
```
Display: Eye contours tracked
EAR Value: Decreasing (< 0.25)
Counter: flag increasing (1, 2, 3...)
Status: Monitoring...
```

### State 4: Drowsiness Confirmed (ALERT!)
```
Condition: flag >= 15 consecutive frames
Display: Large red "ALERT!" text top and bottom
Console: "DROWSINESS ALERT!" printed
Visual: Prominent warning to wake user
```

---

## 📊 Data Flow Diagram

```
User Camera
    ↓
[Video Frame Capture]
    ↓
[Face Detection] → No Face? → Reset counters
    ↓ (Face Found)
[Eye Detection]
    ↓
[Calculate EAR (Eye Aspect Ratio)]
    ↓
{EAR < 0.25?}
    ├─ No → Reset flag counter
    └─ Yes → Increment flag counter
        ↓
    {flag >= 15?}
        ├─ No → Continue monitoring
        └─ Yes → DISPLAY ALERT!
            ↓
    [Show red "ALERT!" on screen]
            ↓
    [Continue until eyes open or user stops]
```

---

## 🔍 What Happens Behind the Scenes

### 1. User Registration
```
Browser Form Submit
    ↓
Flask receives POST /register
    ↓
Validate passwords match
    ↓
Check username uniqueness
    ↓
INSERT into users.db
    ↓
Redirect to /login
```

### 2. User Login
```
Browser Form Submit
    ↓
Flask receives POST /login
    ↓
Query: SELECT * FROM users 
       WHERE username=? AND password=?
    ↓
User found?
    ├─ No → Show error
    └─ Yes → Create session
        ↓
    Store user_id in session
        ↓
    Redirect to /detect
```

### 3. Video Streaming
```
Detect Page Loads
    ↓
Browser requests /video_feed
    ↓
Flask starts generate_frames()
    ↓
Loop:
  ├─ Capture camera frame
  ├─ Detect faces
  ├─ Detect eyes
  ├─ Calculate EAR
  ├─ Check drowsiness
  ├─ Draw alerts if needed
  ├─ Encode as JPEG
  └─ Stream to browser
    ↓
Browser displays MJPEG stream
```

### 4. Logout
```
User clicks "Logout"
    ↓
Flask clears session data
    ↓
Redirect to /login
    ↓
User must re-authenticate
```

---

## 💻 Code-to-Feature Mapping

| Feature | File | Lines/Function |
|---------|------|----------------|
| Login UI | `templates/login.html` | Entire file |
| Registration | `templates/register.html` | Entire file |
| Detection UI | `templates/detect.html` | Entire file |
| Auth Routes | `app.py` | `login()`, `register()` |
| Video Stream | `app.py` | `generate_frames()` |
| Database | `app.py` | `init_db()` |
| EAR Calculation | `app.py` | `eye_aspect_ratio()` |
| Drowsiness Logic | `app.py` | Inside `generate_frames()` |

---

## 🎨 Color Scheme & Design

### Colors Used
```
Primary Gradient: #667eea → #764ba2 (Purple)
Success: #00ff00 (Green for eye contours)
Warning: #ffc107 (Yellow for info boxes)
Danger: #ff0000 (Red for alerts)
Background: #f5f5f5 (Light gray)
Text: #333333 (Dark gray)
```

### Typography
```
Font Family: 'Segoe UI', sans-serif
Headings: 20-28px
Body: 14-16px
Buttons: 16px, bold
```

### Layout
```
Container Width: max 900px
Card Padding: 20-40px
Border Radius: 5-10px
Shadows: Subtle drop shadows
```

---

## 🧪 Testing Scenarios

### Test Case 1: New User Registration
```
1. Visit /login
2. Click "Register here"
3. Enter: username="testuser", password="test123"
4. Confirm password: "test123"
5. Click Register
Expected: Redirect to login with success
```

### Test Case 2: Login Success
```
1. Enter correct credentials
2. Click Login
Expected: Redirect to /detect page
```

### Test Case 3: Login Failure
```
1. Enter wrong password
2. Click Login
Expected: Error message "Invalid username or password"
```

### Test Case 4: Camera Access
```
1. Login successfully
2. Allow camera permissions
Expected: Live video appears in detection page
```

### Test Case 5: Drowsiness Detection
```
1. Position face in front of camera
2. Close eyes for 2-3 seconds
Expected: 
  - Eye contours drawn in green
  - Counter increases
  - After 15 frames: Red "ALERT!" appears
```

### Test Case 6: Logout
```
1. Click "Logout" button
Expected: Session cleared, redirect to login
```

---

## 📱 Mobile View Considerations

While designed for desktop, the app is responsive:

### Desktop (> 768px)
- Full layout with side-by-side features
- Large video feed (500px height)
- Multi-column feature cards

### Mobile (< 768px)
- Stacked layout
- Video feed adjusts to screen width
- Single column feature cards
- Touch-friendly buttons

---

## 🎓 Understanding the Algorithm

### Eye Aspect Ratio (EAR) Formula

```
EAR = (||p2 - p6|| + ||p3 - p5||) / (2 * ||p1 - p4||)

Where:
- p1 to p6 are the 6 facial landmark points around each eye
- ||.|| denotes Euclidean distance
```

### Visual Representation:
```
      p2 ●-------● p3
         \       /
      p1  \     /  p4
           \   /
      p6 ●---● p5

Vertical distances: |p2-p6| and |p3-p5|
Horizontal distance: |p1-p4|
```

### Threshold Values
```
EAR Threshold: 0.25
  - EAR > 0.25 → Eyes OPEN
  - EAR < 0.25 → Eyes CLOSED

Frame Check: 15 frames
  - Must maintain closed state for 15 consecutive frames
  - At ~30 FPS, this equals ~0.5 seconds
```

---

## 🚀 Performance Expectations

### Resource Usage
```
CPU: 20-40% (depends on resolution)
RAM: ~200-300 MB
Camera: 30 FPS typical
Network: Minimal (local streaming)
```

### Detection Speed
```
Face Detection: ~10-30ms per frame
Eye Detection: ~5-15ms per frame
EAR Calculation: < 1ms
Total Latency: ~50-100ms
```

---

## 🎉 Success Indicators

You'll know it's working when:

✅ Login page loads with purple gradient  
✅ Registration creates new user in database  
✅ Login redirects to detection page  
✅ Browser requests camera permission  
✅ Video feed appears in the page  
✅ Green boxes/contours show on face/eyes  
✅ Closing eyes triggers counter increase  
✅ After 15 frames: Red "ALERT!" appears  
✅ Logout returns to login page  

---

**End of Demo Guide** 

For technical details, see `WEB_APPLICATION.md`  
For quick setup, see `QUICK_START.md`
