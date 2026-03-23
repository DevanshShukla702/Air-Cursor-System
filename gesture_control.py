import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time

def main():
    # Setup MediaPipe Hands
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
    hands = mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    )

    # Initialize Camera
    cap = cv2.VideoCapture(0)
    screen_w, screen_h = pyautogui.size()

    # Disable PyAutoGUI failsafe to prevent crashes near screen edges
    pyautogui.FAILSAFE = False

    # Gesture Configuration
    click_threshold = 35  # Pixel distance between thumb and index for a click
    cooldown_time = 0.5   # Seconds
    smooth_factor = 0.4   # Smoothing factor for cursor movement
    
    last_click_time = 0
    prev_x, prev_y = screen_w // 2, screen_h // 2
    
    print("Starting AirCursor System Gesture Control...")
    print("Press 'ESC' in the video window to exit.")

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        # Flip the image horizontally for natural selfie-view behavior
        frame = cv2.flip(frame, 1)
        h, w, c = frame.shape
        
        # Define a centered interaction zone (makes it easier to reach screen edges)
        pad_x, pad_y = int(w * 0.15), int(h * 0.2)
        cv2.rectangle(frame, (pad_x, pad_y), (w - pad_x, h - pad_y), (255, 0, 255), 2)
        
        # Convert BGR image to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the image and find hands
        results = hands.process(rgb_frame)
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                # Get coordinates for Index tip (8) and Thumb tip (4)
                index_tip = hand_landmarks.landmark[8]
                thumb_tip = hand_landmarks.landmark[4]
                
                # Convert normalized coordinates to pixel coordinates
                ix, iy = int(index_tip.x * w), int(index_tip.y * h)
                tx, ty = int(thumb_tip.x * w), int(thumb_tip.y * h)
                
                # Visual Indicator for fingers
                cv2.circle(frame, (ix, iy), 10, (255, 0, 0), cv2.FILLED)
                cv2.circle(frame, (tx, ty), 10, (0, 0, 255), cv2.FILLED)
                cv2.line(frame, (ix, iy), (tx, ty), (0, 255, 255), 2)
                
                # Map index finger position to screen dimensions using the interaction zone
                mapped_x = np.interp(ix, (pad_x, w - pad_x), (0, screen_w))
                mapped_y = np.interp(iy, (pad_y, h - pad_y), (0, screen_h))
                
                # Apply smoothing to the cursor movement
                curr_x = prev_x + (mapped_x - prev_x) * smooth_factor
                curr_y = prev_y + (mapped_y - prev_y) * smooth_factor
                
                # Move the mouse cursor
                try:
                    pyautogui.moveTo(curr_x, curr_y)
                except Exception as e:
                    pass
                
                prev_x, prev_y = curr_x, curr_y
                
                # Calculate the Euclidean distance between thumb and index finger
                distance = np.hypot(tx - ix, ty - iy)
                
                # Perform click action if fingers are close and cooldown has elapsed
                if distance < click_threshold:
                    current_time = time.time()
                    if current_time - last_click_time > cooldown_time:
                        pyautogui.click()
                        last_click_time = current_time
                        cv2.putText(frame, "CLICK", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)

        # Show the video feed with annotations
        cv2.imshow("Hand Tracking Gesture Control", frame)
        
        # Break on 'ESC' key press
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
