import cv2
import numpy as np
import pyautogui as pyag
import mediapipe as mp

# Initialize the MediaPipe Face Mesh module
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Thresholds and consecutive frame length for triggering the mouse action
EYE_AR_THRESH = 0.19  # Threshold for detecting a wink (can be adjusted)
WINK_CONSECUTIVE_FRAMES = 10  # Number of frames needed to confirm a wink

# Initialize variables for tracking winks and cursor movement
WINK_COUNTER_LEFT = 0
WINK_COUNTER_RIGHT = 0
INPUT_MODE = False
ANCHOR_POINT = None

# Colors for drawing on the frame
WHITE_COLOR = (255, 255, 255)
RED_COLOR = (0, 0, 255)
GREEN_COLOR = (0, 255, 0)
BLUE_COLOR = (255, 0, 0)

# Video capture
vid = cv2.VideoCapture(0)
resolution_w = 1366
resolution_h = 768
cam_w = 640
cam_h = 480
unit_w = resolution_w / cam_w
unit_h = resolution_h / cam_h

# Eye aspect ratio (EAR) calculation
def eye_aspect_ratio(eye_landmarks):
    # Calculate the distance between the two vertical eye landmarks
    A = np.linalg.norm(eye_landmarks[1] - eye_landmarks[5])
    B = np.linalg.norm(eye_landmarks[2] - eye_landmarks[4])

    # Calculate the distance between the horizontal eye landmarks
    C = np.linalg.norm(eye_landmarks[0] - eye_landmarks[3])

    # Return the eye aspect ratio
    ear = (A + B) / (2.0 * C)
    return ear

# Smooth scrolling based on eye movement
def scroll_based_on_eye_movement(left_eye_landmarks, right_eye_landmarks):
    left_eye_vertical_movement = np.linalg.norm(left_eye_landmarks[1] - left_eye_landmarks[5])
    right_eye_vertical_movement = np.linalg.norm(right_eye_landmarks[1] - right_eye_landmarks[5])

    # Scroll down if looking down
    if left_eye_vertical_movement > 10:
        pyag.scroll(-10)  # Scroll down
        print("Left eye looking down - Scrolling Down")
    elif right_eye_vertical_movement > 10:
        pyag.scroll(10)  # Scroll up
        print("Right eye looking up - Scrolling Up")

while True:
    _, frame = vid.read()
    frame = cv2.flip(frame, 1)
    frame = cv2.resize(frame, (cam_w, cam_h))
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Perform the facial landmarks detection using MediaPipe
    results = face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            # Extract the required landmarks
            landmarks = np.array([(lm.x * cam_w, lm.y * cam_h) for lm in face_landmarks.landmark])

            left_eye_landmarks = landmarks[[33, 160, 158, 133, 153, 144]]
            right_eye_landmarks = landmarks[[362, 385, 387, 263, 373, 380]]
            mouth_landmarks = landmarks[[61, 291, 78, 308, 13, 14, 17, 0, 267, 57]]  # Placeholder for mouth

            # Calculate the Eye Aspect Ratios for both eyes
            left_eye_ear = eye_aspect_ratio(left_eye_landmarks)
            right_eye_ear = eye_aspect_ratio(right_eye_landmarks)

            # Check for left eye wink (EAR drops below threshold)
            if left_eye_ear < EYE_AR_THRESH:
                WINK_COUNTER_LEFT += 1
            else:
                if WINK_COUNTER_LEFT >= WINK_CONSECUTIVE_FRAMES:
                    # Trigger left-click if a wink is detected for left eye
                    pyag.click(button='left')
                    print("Left wink detected - Left Click")
                WINK_COUNTER_LEFT = 0

            # Check for right eye wink (EAR drops below threshold)
            if right_eye_ear < EYE_AR_THRESH:
                WINK_COUNTER_RIGHT += 1
            else:
                if WINK_COUNTER_RIGHT >= WINK_CONSECUTIVE_FRAMES:
                    # Trigger right-click if a wink is detected for right eye
                    pyag.click(button='right')
                    print("Right wink detected - Right Click")
                WINK_COUNTER_RIGHT = 0

            # Draw the eye landmarks for visual feedback
            for (x, y) in left_eye_landmarks:
                cv2.circle(frame, (int(x), int(y)), 3, GREEN_COLOR)
            for (x, y) in right_eye_landmarks:
                cv2.circle(frame, (int(x), int(y)), 3, GREEN_COLOR)

            # Draw other elements and head movement logic as before
            if not INPUT_MODE:
                ANCHOR_POINT = (int(landmarks[1][0]), int(landmarks[1][1]))  # Initial anchor point at nose
                INPUT_MODE = True
                print("Input mode activated")

            if INPUT_MODE:
                cv2.putText(frame, "READING INPUT!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, RED_COLOR, 2)
                if ANCHOR_POINT is not None:
                    x, y = ANCHOR_POINT
                    current_nose_point = (int(landmarks[1][0]), int(landmarks[1][1]))
                    w, h = 60, 35
                    cv2.rectangle(frame, (x - w, y - h), (x + w, y + h), GREEN_COLOR, 2)
                    cv2.line(frame, ANCHOR_POINT, current_nose_point, BLUE_COLOR, 2)

                    # Faster movement: Increase the amount of movement for relative cursor movement
                    nx, ny = current_nose_point
                    if abs(nx - x) > w:
                        if nx > x:
                            pyag.moveRel(20, 0)  # Increase to 30 pixels for faster movement
                        elif nx < x:
                            pyag.moveRel(-20, 0)
                    if abs(ny - y) > h:
                        if ny > y:
                            pyag.moveRel(0, 20)
                        elif ny < y:
                            pyag.moveRel(0, -20)

            # Smooth scrolling and detect eye movement for scrolling
            scroll_based_on_eye_movement(left_eye_landmarks, right_eye_landmarks)

    else:
        if INPUT_MODE:
            cv2.putText(frame, "READING INPUT!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, RED_COLOR, 2)

    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == 27:  # Press 'Esc' to exit
        break

cv2.destroyAllWindows()
vid.release()
