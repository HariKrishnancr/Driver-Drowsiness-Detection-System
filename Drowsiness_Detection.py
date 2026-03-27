from scipy.spatial import distance
from imutils import face_utils
import imutils
import cv2

def eye_aspect_ratio(eye):
	A = distance.euclidean(eye[1], eye[5])
	B = distance.euclidean(eye[2], eye[4])
	C = distance.euclidean(eye[0], eye[3])
	ear = (A + B) / (2.0 * C)
	return ear
	
thresh = 0.25
frame_check = 15  # Reduced from 20 to make it more sensitive

# Try to use OpenCV's built-in face detector as an alternative to dlib
# Use OpenCV's face detection as fallback
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

# Try to initialize dlib, but continue with OpenCV if it fails
dlib_available = False
try:
    import dlib
    detect = dlib.get_frontal_face_detector()
    predict = dlib.shape_predictor("models/shape_predictor_68_face_landmarks.dat")# Dat file is the crux of the code
    print("Using dlib for face detection and landmark prediction")
    dlib_available = True
except ImportError:
    print("Dlib not available. Using OpenCV Haar cascade as alternative...")
    print("Note: Without dlib, eye aspect ratio calculation won't work properly - using alternative method")

cap=cv2.VideoCapture(0)
flag=0
consecutive_frames_without_eyes = 0  # Counter for frames where eyes aren't detected properly
previous_eyes_count = 0  # Track previous eye detection for comparison

while True:
	ret, frame=cap.read()
	frame = imutils.resize(frame, width=450)
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	
	if dlib_available:
		# Use dlib approach
		subjects = detect(gray, 0)
		for subject in subjects:
			shape = predict(gray, subject)
			shape = face_utils.shape_to_np(shape)#converting to NumPy Array
			(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["left_eye"]
			(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["right_eye"]
			leftEye = shape[lStart:lEnd]
			rightEye = shape[rStart:rEnd]
			leftEAR = eye_aspect_ratio(leftEye)
			rightEAR = eye_aspect_ratio(rightEye)
			ear = (leftEAR + rightEAR) / 2.0
			leftEyeHull = cv2.convexHull(leftEye)
			rightEyeHull = cv2.convHull(rightEye)
			cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
			cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)
			if ear < thresh:
				flag += 1
				print (flag)
				if flag >= frame_check:
					cv2.putText(frame, "****************ALERT!****************", (10, 30),
						cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
					cv2.putText(frame, "****************ALERT!****************", (10,325),
						cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
					#print ("Drowsy")
			else:
				flag = 0
	else:
		# Fallback to OpenCV face detection with improved drowsiness detection
		faces = face_cascade.detectMultiScale(gray, 1.3, 5)
		
		if len(faces) > 0:
			for (x, y, w, h) in faces:
				cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
				roi_gray = gray[y:y+h, x:x+w]
				roi_color = frame[y:y+h, x:x+w]
				
				# Simple eye detection within the face region
				eyes = eye_cascade.detectMultiScale(roi_gray)
				
				# Improved drowsiness detection logic:
				# If eyes are consistently not detected or the number of detected eyes changes frequently,
				# it might indicate drowsiness (closed eyes or head nodding)
				if len(eyes) < 1:  # If no eyes are detected at all
					consecutive_frames_without_eyes += 1
					previous_eyes_count = 0
				elif len(eyes) == 1:  # If only one eye detected (could be partially closed)
					consecutive_frames_without_eyes += 1
					previous_eyes_count = 1
				else:  # If both eyes detected normally
					# Check if eye count changed significantly from previous frame (indicating blinking)
					if abs(len(eyes) - previous_eyes_count) > 1:
						consecutive_frames_without_eyes = max(0, consecutive_frames_without_eyes - 1)  # Reduce counter when eyes are clearly detected
					else:
						consecutive_frames_without_eyes = max(0, consecutive_frames_without_eyes - 1)  # Reduce counter when eyes are clearly detected
					previous_eyes_count = len(eyes)
				
				# Draw rectangles around detected eyes
				for (ex, ey, ew, eh) in eyes:
					cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)
				
				# Trigger alert if consecutive frames without proper eye detection exceed threshold
				if consecutive_frames_without_eyes >= frame_check:
					cv2.putText(frame, "****************ALERT!****************", (10, 30),
						cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
					cv2.putText(frame, "****************ALERT!****************", (10,325),
						cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
					print("DROWSINESS ALERT!")
		else:
			# No face detected, reset counters
			consecutive_frames_without_eyes = 0
			previous_eyes_count = 0
			print("No face detected")
			# Continue the loop to try to detect a face in the next frame
	
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF
	if key == ord("q"):
		break
cv2.destroyAllWindows()
cap.release()