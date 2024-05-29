import cv2
import time
import os
import traceback
import mediapipe as mp
from google.cloud import storage
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from linebot import LineBotApi
from linebot.models import TextSendMessage, ImageSendMessage
from datetime import timedelta
import subprocess

# LINE setup
LINE_ACCESS_TOKEN = os.getenv('LINE_ACCESS_TOKEN')
LINE_USER_ID = os.getenv('LINE_USER_ID')

if LINE_ACCESS_TOKEN is None or LINE_USER_ID is None:
    raise ValueError("LINE_ACCESS_TOKEN or LINE_USER_ID environment variable not set")

line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)

# Google Cloud Storage setup
GOOGLE_APPLICATION_CREDENTIAL = os.getenv('GOOGLE_APPLICATION_CREDENTIAL')
if GOOGLE_APPLICATION_CREDENTIAL is None:
    raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable not set")

credentials = service_account.Credentials.from_service_account_file(GOOGLE_APPLICATION_CREDENTIAL)

def upload_to_bucket(bucket_name, source_file_name, destination_blob_name):
    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)

    url = blob.generate_signed_url(expiration=timedelta(hours=1), method='GET')
    return url

def send_line_message(image_path, text="Detection has stayed over the threshold for more than 10 seconds. See the attached image."):
    try:
        # 調用外部 Python 腳本，並立即返回
        subprocess.Popen(['python', 'D:\\CloudIoT\\CallArduino.py'])
        text_message = TextSendMessage(text=text)
        line_bot_api.push_message(LINE_USER_ID, text_message)
        print("Text message sent successfully!")
        
        bucket_name = 'iot_pro'
        destination_blob_name = os.path.basename(image_path)
        image_url = upload_to_bucket(bucket_name, image_path, destination_blob_name)
        
        image_message = ImageSendMessage(
            original_content_url=image_url,
            preview_image_url=image_url
        )
        line_bot_api.push_message(LINE_USER_ID, image_message)
        print("Image message sent successfully!")
    
    except Exception as e:
        print(f"Failed to send LINE message: {e}")
        traceback.print_exc()

# Load classifiers
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
if face_cascade.empty():
    raise ValueError("Failed to load cascade classifiers.")

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

# Initialize video capture
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise IOError("Cannot open webcam")

# Gesture detection variables
start_time = None
detection_active = False
cooldown_time = 60
last_email_time = 0
threshold = 3
image_path = "last_detection.jpg"
gesture_start_time = None
detected_gesture = ""

def is_thumbs_up(hand_landmarks):
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    thumb_ip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP]
    index_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]
    return thumb_tip.y < thumb_ip.y < index_mcp.y

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4)

        current_max = 0
        for (x, y, w, h) in faces:
            detection_rate = w * h / (frame.shape[0] * frame.shape[1]) * 100
            if detection_rate > current_max:
                current_max = detection_rate
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
            cv2.putText(frame, f'Face: {detection_rate:.2f}%', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        if current_max >= threshold:
            if not detection_active:
                detection_active = True
                start_time = time.time()
            elif time.time() - start_time > 10 and time.time() - last_email_time > cooldown_time:
                if cv2.imwrite(image_path, frame):
                    print("Image written successfully.")
                send_line_message(image_path)
                detection_active = False
                last_email_time = time.time()
        else:
            detection_active = False

        # Hand Gesture Recognition
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb_frame)

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                if is_thumbs_up(hand_landmarks):
                    detected_gesture = "Thumbs Up"
                else:
                    detected_gesture = ""

                if detected_gesture == "Thumbs Up":
                    if gesture_start_time is None:
                        gesture_start_time = time.time()
                    elif time.time() - gesture_start_time > 5:
                        cv2.putText(frame, f'{detected_gesture}!', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                        if cv2.imwrite(image_path, frame):
                            print("Image written successfully.")
                        send_line_message(image_path, text=f"{detected_gesture} detected!")
                        gesture_start_time = None  # Reset gesture start time
                else:
                    gesture_start_time = None

                for lm in hand_landmarks.landmark:
                    h, w, c = frame.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(frame, (cx, cy), 5, (0, 255, 0), cv2.FILLED)
                mp.solutions.drawing_utils.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        cv2.imshow('Detection Window', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    cap.release()
    cv2.destroyAllWindows()