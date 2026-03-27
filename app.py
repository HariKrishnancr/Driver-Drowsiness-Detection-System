from flask import Flask, render_template, request, redirect, url_for, session, Response, jsonify, send_file
import cv2
import mysql.connector
from mysql.connector import Error
import os
import io
from fpdf import FPDF
from scipy.spatial import distance
from imutils import face_utils
import imutils
import numpy as np
import json
import threading
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a secure secret key

# MySQL Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'drowsiness_detection',
    'user': 'root',
    'password': ''  # Default WAMP password is empty, change if needed
}

def get_db_connection():
    """Create and return a database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

class PDFReport(FPDF):
    def header(self):
        # Set dark background for header area (if needed)
        self.set_fill_color(26, 26, 46) # #1a1a2e (website theme)
        self.rect(0, 0, 210, 40, 'F')
        
        self.set_font('helvetica', 'B', 24)
        self.set_text_color(102, 126, 234) # #667eea
        self.cell(0, 20, 'DROWSINESS HISTORY REPORT', border=0, ln=1, align='C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', align='C')

    def chapter_title(self, label):
        self.set_font('helvetica', 'B', 16)
        self.set_fill_color(42, 42, 78) # #2a2a4e
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, label, border=0, ln=1, align='L', fill=True)
        self.ln(5)

    def user_info(self, user_data):
        self.set_font('helvetica', '', 12)
        self.set_text_color(51, 51, 51) # Back to dark for body text on white page
        self.set_fill_color(240, 240, 240)
        self.cell(0, 10, f"User: {user_data['username']}", ln=1, fill=True)
        self.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=1, fill=True)
        self.ln(10)

    def history_table(self, history_data):
        # Table Header
        self.set_font('helvetica', 'B', 12)
        self.set_fill_color(102, 126, 234) # #667eea
        self.set_text_color(255, 255, 255)
        self.cell(20, 10, 'ID', border=1, align='C', fill=True)
        self.cell(60, 10, 'Timestamp', border=1, align='C', fill=True)
        self.cell(60, 10, 'Event Type', border=1, align='C', fill=True)
        self.cell(50, 10, 'Method', border=1, align='C', fill=True)
        self.ln()

        # Table Rows
        self.set_font('helvetica', '', 11)
        self.set_text_color(0, 0, 0)
        fill = False
        for event in history_data:
            self.set_fill_color(240, 240, 240) if fill else self.set_fill_color(255, 255, 255)
            self.cell(20, 10, str(event['id']), border=1, align='C', fill=fill)
            self.cell(60, 10, str(event['timestamp']), border=1, align='C', fill=fill)
            self.cell(60, 10, str(event['event_type']), border=1, align='C', fill=fill)
            self.cell(50, 10, str(event['method']), border=1, align='C', fill=fill)
            self.ln()
            fill = not fill

# Global settings dictionary
detection_settings = {
    'ear_threshold': 0.25,
    'frame_check': 15,
    'sound_alert': True,
    'visual_alert': True,
    'alert_volume': 0.75,
    'show_landmarks': True,
    'show_stats': True
}

# Lock for thread-safe settings access
settings_lock = threading.Lock()
alert_states = {}
alert_states_lock = threading.Lock()

# Database initialization
def init_db():
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = connection.cursor()
        
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        cursor.execute(f"USE {DB_CONFIG['database']}")
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP NULL DEFAULT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                admin_email VARCHAR(150) NULL,
                admin_app_password VARCHAR(100) NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        # Migration for existing admins table
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.columns
            WHERE table_schema=%s AND table_name='admins' AND column_name='admin_email'
        """, (DB_CONFIG['database'],))
        if cursor.fetchone()[0] == 0:
            cursor.execute("ALTER TABLE admins ADD COLUMN admin_email VARCHAR(150) NULL")
        
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.columns
            WHERE table_schema=%s AND table_name='admins' AND column_name='admin_app_password'
        """, (DB_CONFIG['database'],))
        if cursor.fetchone()[0] == 0:
            cursor.execute("ALTER TABLE admins ADD COLUMN admin_app_password VARCHAR(100) NULL")
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS drivers (
                user_id INT PRIMARY KEY,
                status VARCHAR(20) DEFAULT 'pending',
                alert_count INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_drivers_user
                    FOREIGN KEY (user_id) REFERENCES users(id)
                    ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        # Migration for existing drivers table
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.columns
            WHERE table_schema=%s AND table_name='drivers' AND column_name='status'
        """, (DB_CONFIG['database'],))
        if cursor.fetchone()[0] == 0:
            cursor.execute("ALTER TABLE drivers ADD COLUMN status VARCHAR(20) DEFAULT 'pending'")

        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.columns
            WHERE table_schema=%s AND table_name='drivers' AND column_name='alert_count'
        """, (DB_CONFIG['database'],))
        if cursor.fetchone()[0] == 0:
            cursor.execute("ALTER TABLE drivers ADD COLUMN alert_count INT DEFAULT 0")

        # Ensure every existing user has a driver record
        cursor.execute("""
            INSERT IGNORE INTO drivers (user_id, status)
            SELECT id, 'approved' FROM users
        """)

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NULL,
                mode VARCHAR(10) NOT NULL,
                username VARCHAR(50) NULL,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ended_at TIMESTAMP NULL,
                INDEX (user_id),
                CONSTRAINT fk_sessions_user
                    FOREIGN KEY (user_id) REFERENCES users(id)
                    ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS drowsiness_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NULL,
                session_id INT NULL,
                event_type VARCHAR(50) NOT NULL,
                ear FLOAT NULL,
                frame_count INT NULL,
                method VARCHAR(20) NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX (user_id),
                INDEX (session_id),
                CONSTRAINT fk_history_user
                    FOREIGN KEY (user_id) REFERENCES users(id)
                    ON DELETE SET NULL,
                CONSTRAINT fk_history_session
                    FOREIGN KEY (session_id) REFERENCES sessions(id)
                    ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trials_used (
                id INT AUTO_INCREMENT PRIMARY KEY,
                session_id INT NULL,
                ip_address VARCHAR(100) NULL,
                user_agent VARCHAR(255) NULL,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ended_at TIMESTAMP NULL,
                INDEX (session_id),
                CONSTRAINT fk_trials_session
                    FOREIGN KEY (session_id) REFERENCES sessions(id)
                    ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedbacks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NULL,
                name VARCHAR(100) NULL,
                email VARCHAR(150) NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX (user_id),
                CONSTRAINT fk_feedback_user
                    FOREIGN KEY (user_id) REFERENCES users(id)
                    ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.columns
            WHERE table_schema=%s AND table_name='drowsiness_history' AND column_name='event_type'
        """, (DB_CONFIG['database'],))
        if cursor.fetchone()[0] == 0:
            cursor.execute("ALTER TABLE drowsiness_history ADD COLUMN event_type VARCHAR(50) NOT NULL DEFAULT 'alert'")
        
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.columns
            WHERE table_schema=%s AND table_name='drowsiness_history' AND column_name='method'
        """, (DB_CONFIG['database'],))
        if cursor.fetchone()[0] == 0:
            cursor.execute("ALTER TABLE drowsiness_history ADD COLUMN method VARCHAR(20) NULL")
        
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.columns
            WHERE table_schema=%s AND table_name='drowsiness_history' AND column_name='ear'
        """, (DB_CONFIG['database'],))
        if cursor.fetchone()[0] == 0:
            cursor.execute("ALTER TABLE drowsiness_history ADD COLUMN ear FLOAT NULL")
        
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.columns
            WHERE table_schema=%s AND table_name='drowsiness_history' AND column_name='frame_count'
        """, (DB_CONFIG['database'],))
        if cursor.fetchone()[0] == 0:
            cursor.execute("ALTER TABLE drowsiness_history ADD COLUMN frame_count INT NULL")
        
        # Ensure session_id column exists for joins with sessions
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.columns
            WHERE table_schema=%s AND table_name='drowsiness_history' AND column_name='session_id'
        """, (DB_CONFIG['database'],))
        if cursor.fetchone()[0] == 0:
            cursor.execute("ALTER TABLE drowsiness_history ADD COLUMN session_id INT NULL")
            cursor.execute("""
                SELECT COUNT(*) FROM information_schema.statistics
                WHERE table_schema=%s AND table_name='drowsiness_history' AND index_name='idx_dh_session_id'
            """, (DB_CONFIG['database'],))
            if cursor.fetchone()[0] == 0:
                cursor.execute("CREATE INDEX idx_dh_session_id ON drowsiness_history (session_id)")
        
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.columns
            WHERE table_schema=%s AND table_name='drowsiness_history' AND column_name='timestamp'
        """, (DB_CONFIG['database'],))
        if cursor.fetchone()[0] == 0:
            cursor.execute("ALTER TABLE drowsiness_history ADD COLUMN timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.views
            WHERE table_schema=%s AND table_name='detection_history'
        """, (DB_CONFIG['database'],))
        if cursor.fetchone()[0] == 0:
            try:
                cursor.execute("CREATE VIEW detection_history AS SELECT id, user_id, session_id, event_type, ear, frame_count, method, timestamp FROM drowsiness_history")
            except Exception as e:
                print(f"Create view detection_history failed: {e}")
        
        cursor.execute("SELECT COUNT(*) FROM admins")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO admins (username, password) VALUES (%s, %s)", ('admin', 'admin123'))
        
        connection.commit()
        print("Database initialized successfully")
        
    except Error as e:
        print(f"Error initializing database: {e}")
    finally:
        try:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
        except Exception:
            pass

# Drowsiness Detection Logic
def eye_aspect_ratio(eye):
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

thresh = 0.25
frame_check = 15

# Try to use OpenCV's built-in face detector as an alternative to dlib
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

# Try to initialize dlib, but continue with OpenCV if it fails
dlib_available = False
try:
    # import dlib
    detect = dlib.get_frontal_face_detector()
    predict = dlib.shape_predictor("models/shape_predictor_68_face_landmarks.dat")
    print("Using dlib for face detection and landmark prediction")
    dlib_available = True
except ImportError:
    print("Dlib not available. Using OpenCV Haar cascade as alternative...")
    dlib_available = False
except Exception as e:
    print(f"Dlib error: {e}. Using OpenCV Haar cascade as alternative...")
    dlib_available = False

def generate_frames(session_key, current_user_id, current_session_id):
    global detection_settings
    
    cap = cv2.VideoCapture(0)
    flag = 0
    consecutive_frames_without_eyes = 0
    previous_eyes_count = 0
    alert_logged = False
    is_drowsy = False
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Get current settings (thread-safe)
        with settings_lock:
            current_thresh = detection_settings['ear_threshold']
            current_frame_check = detection_settings['frame_check']
            show_landmarks = detection_settings['show_landmarks']
        
        frame = imutils.resize(frame, width=450)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        if dlib_available:
            subjects = detect(gray, 0)
            
            # Check if alert is latched
            with alert_states_lock:
                latched = alert_states.get(session_key, False)
            
            if len(subjects) == 0:
                flag = 0
                # If latched, don't automatically reset is_drowsy to False
                if not latched:
                    if is_drowsy:
                        with alert_states_lock:
                            alert_states[session_key] = False
                        is_drowsy = False
            for subject in subjects:
                shape = predict(gray, subject)
                shape = face_utils.shape_to_np(shape)
                (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["left_eye"]
                (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["right_eye"]
                leftEye = shape[lStart:lEnd]
                rightEye = shape[rStart:rEnd]
                leftEAR = eye_aspect_ratio(leftEye)
                rightEAR = eye_aspect_ratio(rightEye)
                ear = (leftEAR + rightEAR) / 2.0
                leftEyeHull = cv2.convexHull(leftEye)
                rightEyeHull = cv2.convexHull(rightEye)
                if show_landmarks:
                    cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
                    cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)
                
                # If alert is latched, show alert message and skip new detection until reset
                if latched:
                    with settings_lock:
                        visual_alert = detection_settings['visual_alert']
                    if visual_alert:
                        cv2.putText(frame, "****************ALERT!****************", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        cv2.putText(frame, "****************ALERT!****************", (10, 325),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        cv2.putText(frame, "CLICK RESET TO CONTINUE", (10, 180),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    continue

                if ear < current_thresh:
                    flag += 1
                    if flag >= frame_check:
                        # Check if visual alert is enabled
                        with settings_lock:
                            visual_alert = detection_settings['visual_alert']
                        
                        if visual_alert:
                            cv2.putText(frame, "****************ALERT!****************", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                            cv2.putText(frame, "****************ALERT!****************", (10, 325),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        if not is_drowsy:
                            with alert_states_lock:
                                alert_states[session_key] = True
                            is_drowsy = True
                        if not alert_logged:
                            try:
                                connection = get_db_connection()
                                if connection and current_session_id:
                                    cursor = connection.cursor()
                                    cursor.execute('''
                                        INSERT INTO drowsiness_history (user_id, session_id, event_type, ear, frame_count, method)
                                        VALUES (%s, %s, %s, %s, %s, %s)
                                    ''', (
                                        current_user_id,
                                        current_session_id,
                                        'alert',
                                        float(ear),
                                        int(current_frame_check),
                                        'dlib'
                                    ))
                                    # Increment persistent alert_count for the driver
                                    if current_user_id:
                                        print(f"Incrementing alert_count for user {current_user_id} (dlib)")
                                        cursor.execute('''
                                            UPDATE drivers SET alert_count = alert_count + 1 WHERE user_id = %s
                                        ''', (current_user_id,))
                                        print(f"Update row count: {cursor.rowcount}")
                                    connection.commit()
                                    cursor.close()
                                    connection.close()
                            except Exception as e:
                                print(f"Error logging alert (dlib): {e}")
                            alert_logged = True
                else:
                    flag = 0
                    alert_logged = False
                    # Only reset internal is_drowsy, but DO NOT reset alert_states[session_key] 
                    # because we want it to stay latched until the manual reset button is clicked.
                    if is_drowsy:
                        print("Resetting internal is_drowsy (dlib)")
                    is_drowsy = False
        else:
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            
            # Check if alert is latched
            with alert_states_lock:
                latched = alert_states.get(session_key, False)

            if len(faces) > 0:
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                    roi_gray = gray[y:y+h, x:x+w]
                    roi_color = frame[y:y+h, x:x+w]
                    
                    eyes = eye_cascade.detectMultiScale(roi_gray)
                    
                    # If latched, show alert and skip detection
                    if latched:
                        cv2.putText(frame, "****************ALERT!****************", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        cv2.putText(frame, "****************ALERT!****************", (10, 325),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        cv2.putText(frame, "CLICK RESET TO CONTINUE", (10, 180),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        continue

                    if len(eyes) < 1:
                        consecutive_frames_without_eyes += 1
                        previous_eyes_count = 0
                    elif len(eyes) == 1:
                        consecutive_frames_without_eyes += 1
                        previous_eyes_count = 1
                    else:
                        if abs(len(eyes) - previous_eyes_count) > 1:
                            consecutive_frames_without_eyes = max(0, consecutive_frames_without_eyes - 1)
                        else:
                            consecutive_frames_without_eyes = max(0, consecutive_frames_without_eyes - 1)
                        previous_eyes_count = len(eyes)
                        
                        # Reset alert_logged when eyes are detected
                        alert_logged = False
                        if is_drowsy:
                            with alert_states_lock:
                                # We still latch the alert_states for the UI button, 
                                # but internal is_drowsy is False so it can trigger again.
                                pass
                            is_drowsy = False
                    
                    for (ex, ey, ew, eh) in eyes:
                        cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)
                    
                    if consecutive_frames_without_eyes >= frame_check:
                        cv2.putText(frame, "****************ALERT!****************", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        cv2.putText(frame, "****************ALERT!****************", (10, 325),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        if not is_drowsy:
                            with alert_states_lock:
                                alert_states[session_key] = True
                            is_drowsy = True
                        if not alert_logged:
                            try:
                                connection = get_db_connection()
                                if connection and current_session_id:
                                    cursor = connection.cursor()
                                    cursor.execute('''
                                        INSERT INTO drowsiness_history (user_id, session_id, event_type, ear, frame_count, method)
                                        VALUES (%s, %s, %s, %s, %s, %s)
                                    ''', (
                                        current_user_id,
                                        current_session_id,
                                        'alert',
                                        None,
                                        int(frame_check),
                                        'opencv'
                                    ))
                                    # Increment persistent alert_count for the driver
                                    if current_user_id:
                                        print(f"Incrementing alert_count for user {current_user_id} (opencv)")
                                        cursor.execute('''
                                            UPDATE drivers SET alert_count = alert_count + 1 WHERE user_id = %s
                                        ''', (current_user_id,))
                                        print(f"Update row count (opencv): {cursor.rowcount}")
                                    connection.commit()
                                    cursor.close()
                                    connection.close()
                            except Exception as e:
                                print(f"Error logging alert (opencv): {e}")
                            alert_logged = True
            else:
                consecutive_frames_without_eyes = 0
                previous_eyes_count = 0
                alert_logged = False
                # Reset internal is_drowsy, but DO NOT reset alert_states[session_key]
                # so it stays latched until the manual reset button is clicked.
                is_drowsy = False
        
        # Encode frame for web streaming
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    
    cap.release()

@app.route('/')
def index():
    # Show the new index page with introduction
    return render_template('index.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        try:
            connection = get_db_connection()
            if connection:
                cursor = connection.cursor(dictionary=True)
                cursor.execute('SELECT * FROM admins WHERE username = %s AND password = %s', (username, password))
                admin = cursor.fetchone()
                cursor.close()
                connection.close()
                if admin:
                    session['admin_id'] = admin['id']
                    session['admin_username'] = admin['username']
                    session['is_admin'] = True
                    return redirect(url_for('admin_dashboard'))
        except Exception as e:
            print(f"Admin login error: {e}")
        return render_template('admin_login.html', error='Invalid admin credentials')
    
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            
            # Get all users with their driver status
            cursor.execute('''
                SELECT u.*, d.status as driver_status, d.alert_count 
                FROM users u
                LEFT JOIN drivers d ON u.id = d.user_id
                ORDER BY u.created_at DESC
            ''')
            users = cursor.fetchall()
            
            # Get statistics
            cursor.execute('SELECT COUNT(*) as total FROM users')
            total_users = cursor.fetchone()['total']
            
            cursor.execute('SELECT COUNT(*) as active FROM users WHERE last_login IS NOT NULL')
            active_users = cursor.fetchone()['active']
            
            cursor.execute('SELECT COUNT(*) as cnt FROM drowsiness_history')
            total_drowsy_events = cursor.fetchone()['cnt']
            
            cursor.execute('SELECT COUNT(*) as cnt FROM drowsiness_history WHERE DATE(timestamp) = CURDATE()')
            alerts_today = cursor.fetchone()['cnt']

            # Get pending approvals count
            cursor.execute("SELECT COUNT(*) as cnt FROM drivers WHERE status = 'pending'")
            pending_approvals = cursor.fetchone()['cnt']
            
            cursor.execute('''
                SELECT dh.id, dh.timestamp, dh.method, dh.event_type, s.mode, s.username AS session_username, dh.user_id 
                FROM drowsiness_history dh
                LEFT JOIN sessions s ON dh.session_id = s.id
                ORDER BY dh.timestamp DESC
                LIMIT 10
            ''')
            recent_history = cursor.fetchall()

            # Get admin's current email configuration
            cursor.execute('SELECT admin_email, admin_app_password FROM admins WHERE id = %s', (session['admin_id'],))
            admin_config = cursor.fetchone()
            
            cursor.close()
            connection.close()
            
            return render_template('admin_dashboard.html', 
                                 users=users,
                                 total_users=total_users,
                                 active_users=active_users,
                                 total_drowsy_events=total_drowsy_events,
                                 alerts_today=alerts_today,
                                 pending_approvals=pending_approvals,
                                 recent_history=recent_history,
                                 admin_username=session['admin_username'],
                                 admin_email=admin_config.get('admin_email'),
                                 has_app_password=bool(admin_config.get('admin_app_password')))
        else:
            return "Database connection error", 500
    except Exception as e:
        print(f"Admin dashboard error: {e}")
        return str(e), 500

@app.route('/admin/approvals')
def admin_approvals():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            
            # Get pending drivers
            cursor.execute('''
                SELECT u.id, u.username, u.created_at, d.status
                FROM users u
                JOIN drivers d ON u.id = d.user_id
                WHERE d.status = 'pending'
                ORDER BY u.created_at DESC
            ''')
            pending_drivers = cursor.fetchall()
            
            cursor.close()
            connection.close()
            
            return render_template('admin_approvals.html', 
                                 pending_drivers=pending_drivers,
                                 admin_username=session['admin_username'])
        else:
            return "Database connection error", 500
    except Exception as e:
        print(f"Admin approvals error: {e}")
        return str(e), 500

@app.route('/admin/approve_driver/<int:user_id>', methods=['POST'])
def approve_driver(user_id):
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE drivers SET status = 'approved' WHERE user_id = %s", (user_id,))
            connection.commit()
            cursor.close()
            connection.close()
            return redirect(url_for('admin_approvals'))
        else:
            return "Database connection error", 500
    except Exception as e:
        print(f"Approve driver error: {e}")
        return str(e), 500

@app.route('/admin/reject_driver/<int:user_id>', methods=['POST'])
def reject_driver(user_id):
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE drivers SET status = 'rejected' WHERE user_id = %s", (user_id,))
            connection.commit()
            cursor.close()
            connection.close()
            return redirect(url_for('admin_approvals'))
        else:
            return "Database connection error", 500
    except Exception as e:
        print(f"Reject driver error: {e}")
        return str(e), 500

@app.route('/admin/update_email', methods=['POST'])
def update_admin_email():
    if not session.get('is_admin'):
        return jsonify({'success': False, 'error': 'Not authorized'})
    
    email = request.form.get('admin_email')
    app_password = request.form.get('admin_app_password')
    
    if not email or not app_password:
        return jsonify({'success': False, 'error': 'Email and App Password are required'})
    
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute('''
                UPDATE admins SET admin_email = %s, admin_app_password = %s WHERE id = %s
            ''', (email, app_password, session['admin_id']))
            connection.commit()
            cursor.close()
            connection.close()
            return redirect(url_for('admin_dashboard'))
    except Exception as e:
        print(f"Update admin email error: {e}")
        return jsonify({'success': False, 'error': str(e)})
    
    return jsonify({'success': False, 'error': 'Database error'})

@app.route('/driver/emergency', methods=['POST'])
def driver_emergency():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'})
    
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            # Get admin config
            cursor.execute('SELECT admin_email, admin_app_password FROM admins LIMIT 1')
            admin = cursor.fetchone()
            
            if not admin or not admin['admin_email'] or not admin['admin_app_password']:
                cursor.close()
                connection.close()
                return jsonify({'success': False, 'error': 'Admin has not configured email settings'})
            
            # Send email
            sender_email = admin['admin_email']
            sender_password = admin['admin_app_password']
            receiver_email = admin['admin_email'] # Send to admin themselves
            
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = receiver_email
            msg['Subject'] = f"🚨 EMERGENCY: Driver {session.get('username')} feels sick!"
            
            body = f"""
            Emergency Alert!
            
            Driver: {session.get('username')}
            User ID: {session.get('user_id')}
            Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            Message: The driver has reported that they feel sick and may need assistance.
            
            Please check on the driver immediately.
            """
            msg.attach(MIMEText(body, 'plain'))
            
            # Use Gmail SMTP
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            try:
                server.login(sender_email, sender_password)
            except smtplib.SMTPAuthenticationError as auth_err:
                print(f"SMTP Auth Error: {auth_err}")
                if auth_err.smtp_code == 534:
                    return jsonify({'success': False, 'error': 'Gmail App Password required. Please generate a 16-digit App Password in your Google Account settings.'})
                return jsonify({'success': False, 'error': 'Invalid Gmail credentials. Ensure you are using an App Password.'})
            
            text = msg.as_string()
            server.sendmail(sender_email, receiver_email, text)
            server.quit()
            
            cursor.close()
            connection.close()
            return jsonify({'success': True, 'message': 'Emergency alert sent to admin!'})
            
    except Exception as e:
        print(f"Emergency email error: {e}")
        return jsonify({'success': False, 'error': str(e)})
    
    return jsonify({'success': False, 'error': 'Unknown error'})

@app.route('/admin/user/<int:user_id>')
def view_user_history(user_id):
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            
            # Get user details
            cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
            user = cursor.fetchone()
            
            if not user:
                return "User not found", 404
            
            # Get user's drowsiness history (placeholder for now)
            cursor.execute('''
                SELECT * FROM drowsiness_history 
                WHERE user_id = %s 
                ORDER BY timestamp DESC 
                LIMIT 100
            ''', (user_id,))
            history = cursor.fetchall()
            
            cursor.close()
            connection.close()
            
            return render_template('user_history.html', user=user, history=history)
        else:
            return "Database connection error", 500
    except Exception as e:
        print(f"View user history error: {e}")
        return str(e), 500

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute('DELETE FROM users WHERE id = %s', (user_id,))
            connection.commit()
            cursor.close()
            connection.close()
            
            return redirect(url_for('admin_dashboard'))
        else:
            return "Database connection error", 500
    except Exception as e:
        print(f"Delete user error: {e}")
        return str(e), 500

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    session.pop('admin_username', None)
    session.pop('is_admin', None)
    return redirect(url_for('admin_login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute('''
                SELECT u.*, d.status 
                FROM users u 
                LEFT JOIN drivers d ON u.id = d.user_id 
                WHERE u.username = %s AND u.password = %s
            ''', (username, password))
            user = cursor.fetchone()
            
            if user:
                # Check driver status
                if user['status'] == 'pending':
                    cursor.close()
                    connection.close()
                    return render_template('login.html', error='Your account is pending approval by the admin.')
                elif user['status'] == 'rejected':
                    cursor.close()
                    connection.close()
                    return render_template('login.html', error='Your account registration has been rejected.')

                session['user_id'] = user['id']
                session['username'] = user['username']
                session.pop('trial', None)
                
                # Update last login timestamp
                cursor.execute('UPDATE users SET last_login = NOW() WHERE id = %s', (user['id'],))
                connection.commit()
                
                cursor.close()
                connection.close()
                return redirect(url_for('driver_home'))
            else:
                cursor.close()
                connection.close()
                return render_template('login.html', error='Invalid username or password')
        else:
            return render_template('login.html', error='Database connection error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match')
        
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                
                # Check if username already exists
                cursor.execute('SELECT id FROM users WHERE username = %s', (username,))
                existing_user = cursor.fetchone()
                
                if existing_user:
                    cursor.close()
                    connection.close()
                    return render_template('register.html', error='Username already exists')
                
                # Insert new user
                cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, password))
                connection.commit()
                
                new_user_id = cursor.lastrowid
                try:
                    cursor.execute('INSERT INTO drivers (user_id) VALUES (%s)', (new_user_id,))
                    connection.commit()
                except Exception as e:
                    print(f"Driver insert failed: {e}")
                
                cursor.close()
                connection.close()
                return redirect(url_for('login'))
            
            except Error as e:
                print(f"Error registering user: {e}")
                return render_template('register.html', error='Error creating account. Please try again.')
        else:
            return render_template('register.html', error='Database connection error')
    
    return render_template('register.html')

@app.route('/driver/home')
def driver_home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            
            # Get driver details and stats
            cursor.execute('''
                SELECT u.username, d.alert_count, d.created_at, u.last_login
                FROM users u
                JOIN drivers d ON u.id = d.user_id
                WHERE u.id = %s
            ''', (session['user_id'],))
            driver_stats = cursor.fetchone()
            
            # Get recent drowsiness events
            cursor.execute('''
                SELECT timestamp, event_type, method
                FROM drowsiness_history
                WHERE user_id = %s
                ORDER BY timestamp DESC
                LIMIT 5
            ''', (session['user_id'],))
            recent_events = cursor.fetchall()
            
            # Get total sessions count
            cursor.execute('SELECT COUNT(*) as session_count FROM sessions WHERE user_id = %s', (session['user_id'],))
            total_sessions = cursor.fetchone()['session_count']
            
            cursor.close()
            connection.close()
            
            # Fun/Interesting analysis stuff based on stats
            analysis_msg = ""
            if driver_stats['alert_count'] == 0:
                analysis_msg = "🌟 Perfect record! You're a safety champion."
            elif driver_stats['alert_count'] < 5:
                analysis_msg = "👍 Great job! Keep maintaining that focus."
            else:
                analysis_msg = "🛡️ Safety first! Remember to take regular breaks."

            return render_template('driver_home.html', 
                                 stats=driver_stats, 
                                 events=recent_events, 
                                 total_sessions=total_sessions,
                                 analysis_msg=analysis_msg)
    except Exception as e:
        print(f"Driver home error: {e}")
        return str(e), 500
    
    return redirect(url_for('login'))

@app.route('/trial')
def trial():
    session.clear()
    session['trial'] = True
    session['username'] = 'Trial Mode'
    return redirect(url_for('detect'))

@app.route('/detect')
def detect():
    if 'user_id' not in session and not session.get('trial'):
        return redirect(url_for('login'))
    # Start session log if not started
    try:
        if not session.get('session_log_id'):
            connection = get_db_connection()
            if connection:
                cursor = connection.cursor()
                mode = 'driver' if session.get('user_id') else 'trial'
                username = session.get('username')
                cursor.execute('''
                    INSERT INTO sessions (user_id, mode, username)
                    VALUES (%s, %s, %s)
                ''', (session.get('user_id'), mode, username))
                connection.commit()
                session_id = cursor.lastrowid
                session['session_log_id'] = session_id
                if mode == 'trial':
                    try:
                        ip = request.remote_addr
                        ua = request.headers.get('User-Agent')
                        cursor.execute('''
                            INSERT INTO trials_used (session_id, ip_address, user_agent)
                            VALUES (%s, %s, %s)
                        ''', (session_id, ip, ua))
                        connection.commit()
                        session['trial_usage_id'] = cursor.lastrowid
                    except Exception as e:
                        print(f"Trial usage insert failed: {e}")
                cursor.close()
                connection.close()
    except Exception as e:
        print(f"Error starting session log: {e}")
    return render_template('detect.html', username=session.get('username', 'Driver'), trial=session.get('trial', False))

@app.route('/video_feed')
def video_feed():
    if 'user_id' not in session and not session.get('trial'):
        return redirect(url_for('login'))
    skey = session.get('session_log_id') or session.get('username') or 'anon'
    uid = session.get('user_id')
    sid = session.get('session_log_id')
    return Response(generate_frames(skey, uid, sid), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/alert_status')
def alert_status():
    if 'user_id' not in session and not session.get('trial'):
        return jsonify({'success': False, 'error': 'Not authenticated'})
    
    skey = session.get('session_log_id') or session.get('username') or 'anon'
    with alert_states_lock:
        d = bool(alert_states.get(skey, False))
    
    # Get the latest persistent alert count
    alert_count = 0
    if session.get('user_id'):
        try:
            connection = get_db_connection()
            if connection:
                cursor = connection.cursor(dictionary=True)
                cursor.execute('SELECT alert_count FROM drivers WHERE user_id = %s', (session.get('user_id'),))
                row = cursor.fetchone()
                if row:
                    alert_count = row['alert_count']
                cursor.close()
                connection.close()
        except Exception as e:
            print(f"Error fetching alert count: {e}")
            
    return jsonify({
        'success': True, 
        'drowsy': d,
        'alert_count': alert_count
    })

@app.route('/reset_alert', methods=['POST'])
def reset_alert():
    if 'user_id' not in session and not session.get('trial'):
        return jsonify({'success': False, 'error': 'Not authenticated'})
    skey = session.get('session_log_id') or session.get('username') or 'anon'
    with alert_states_lock:
        alert_states[skey] = False
    return jsonify({'success': True})

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    success = None
    error = None
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        message = request.form.get('message', '').strip()
        if not message:
            error = 'Message is required'
        else:
            try:
                connection = get_db_connection()
                if connection:
                    cursor = connection.cursor()
                    cursor.execute('''
                        INSERT INTO feedbacks (user_id, name, email, message)
                        VALUES (%s, %s, %s, %s)
                    ''', (session.get('user_id'), name if name else None, email if email else None, message))
                    connection.commit()
                    cursor.close()
                    connection.close()
                    success = 'Thank you for your feedback!'
                else:
                    error = 'Database connection error'
            except Exception as e:
                error = 'Failed to submit feedback'
                print(f"Feedback insert error: {e}")
    rows = []
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute('SELECT name, message, created_at FROM feedbacks ORDER BY created_at DESC LIMIT 20')
            rows = cursor.fetchall()
            cursor.close()
            connection.close()
    except Exception as e:
        print(f"Feedback fetch error: {e}")
    return render_template('feedback.html', error=error, success=success, feedbacks=rows)

@app.route('/update_settings', methods=['POST'])
def update_settings():
    global detection_settings
    
    if 'user_id' not in session and not session.get('trial'):
        return jsonify({'success': False, 'error': 'Not authenticated'})
    
    try:
        data = request.get_json()
        
        # Validate and update settings
        with settings_lock:
            if 'ear_threshold' in data:
                ear_thresh = float(data['ear_threshold'])
                if 0.15 <= ear_thresh <= 0.35:
                    detection_settings['ear_threshold'] = ear_thresh
            
            if 'frame_check' in data:
                frame_count = int(data['frame_check'])
                if 5 <= frame_count <= 60:
                    detection_settings['frame_check'] = frame_count
            
            if 'sound_alert' in data:
                detection_settings['sound_alert'] = bool(data['sound_alert'])
            
            if 'visual_alert' in data:
                detection_settings['visual_alert'] = bool(data['visual_alert'])
            
            if 'alert_volume' in data:
                volume = float(data['alert_volume'])
                if 0 <= volume <= 1:
                    detection_settings['alert_volume'] = volume
            
            if 'show_landmarks' in data:
                detection_settings['show_landmarks'] = bool(data['show_landmarks'])
            
            if 'show_stats' in data:
                detection_settings['show_stats'] = bool(data['show_stats'])
        
        print(f"Settings updated: {detection_settings}")
        return jsonify({'success': True, 'settings': detection_settings})
    
    except Exception as e:
        print(f"Error updating settings: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/get_settings', methods=['GET'])
def get_settings():
    if 'user_id' not in session and not session.get('trial'):
        return jsonify({'success': False, 'error': 'Not authenticated'})
    
    with settings_lock:
        return jsonify({'success': True, 'settings': detection_settings})

@app.route('/logout')
def logout():
    try:
        if session.get('session_log_id'):
            connection = get_db_connection()
            if connection:
                cursor = connection.cursor()
                cursor.execute('UPDATE sessions SET ended_at = NOW() WHERE id = %s', (session.get('session_log_id'),))
                if session.get('trial_usage_id'):
                    try:
                        cursor.execute('UPDATE trials_used SET ended_at = NOW() WHERE id = %s', (session.get('trial_usage_id'),))
                    except Exception as e:
                        print(f"Trial usage end update failed: {e}")
                connection.commit()
                cursor.close()
                connection.close()
    except Exception as e:
        print(f"Error ending session log: {e}")
    session.clear()
    return redirect(url_for('index'))

@app.route('/driver/download_report')
def download_driver_report():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            # Get user details
            cursor.execute('SELECT * FROM users WHERE id = %s', (session['user_id'],))
            user = cursor.fetchone()
            # Get user's drowsiness history
            cursor.execute('SELECT * FROM drowsiness_history WHERE user_id = %s ORDER BY timestamp DESC', (session['user_id'],))
            history = cursor.fetchall()
            cursor.close()
            connection.close()

            pdf = PDFReport()
            pdf.alias_nb_pages()
            pdf.add_page()
            pdf.user_info(user)
            pdf.chapter_title('Drowsiness Events History')
            pdf.history_table(history)
            
            # Output to BytesIO
            output = io.BytesIO()
            pdf_content = pdf.output()
            output.write(pdf_content)
            output.seek(0)
            
            return send_file(output, 
                             as_attachment=True, 
                             download_name=f"drowsiness_report_{user['username']}.pdf",
                             mimetype='application/pdf')
    except Exception as e:
        print(f"Driver download report error: {e}")
        return str(e), 500
    return "Error generating report", 500

@app.route('/admin/download_report/<int:user_id>')
def download_admin_report(user_id):
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))

    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            # Get user details
            cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
            user = cursor.fetchone()
            if not user:
                return "User not found", 404
            # Get user's drowsiness history
            cursor.execute('SELECT * FROM drowsiness_history WHERE user_id = %s ORDER BY timestamp DESC', (user_id,))
            history = cursor.fetchall()
            cursor.close()
            connection.close()

            pdf = PDFReport()
            pdf.alias_nb_pages()
            pdf.add_page()
            pdf.user_info(user)
            pdf.chapter_title('Drowsiness Events History')
            pdf.history_table(history)
            
            # Output to BytesIO
            output = io.BytesIO()
            pdf_content = pdf.output()
            output.write(pdf_content)
            output.seek(0)
            
            return send_file(output, 
                             as_attachment=True, 
                             download_name=f"admin_report_{user['username']}.pdf",
                             mimetype='application/pdf')
    except Exception as e:
        print(f"Admin download report error: {e}")
        return str(e), 500
    return "Error generating report", 500

if __name__ == '__main__':
    init_db()
    # For WAMP: Access via http://localhost/Drowsiness_Detection-master
    app.run(debug=True, host='127.0.0.1', port=5000)
