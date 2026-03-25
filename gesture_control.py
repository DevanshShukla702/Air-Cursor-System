import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time
from collections import deque

def is_finger_up(tip, joint):
    """
    Returns True if the finger tip is physically higher (lower y value) 
    than its corresponding lower joint in the camera frame.
    """
    return tip.y < joint.y

class SwipeTracker:
    def __init__(self, min_dist=120, max_time=0.7):
        self.buffer = deque(maxlen=30)
        self.min_dist = min_dist
        self.max_time = max_time

    def add_point(self, x, y):
        current_time = time.time()
        self.buffer.append((x, y, current_time))
        # Drop points older than max_time
        while self.buffer and current_time - self.buffer[0][2] > self.max_time:
            self.buffer.popleft()

    def check_swipe(self):
        if len(self.buffer) < 5:
            return None, 0, 0
            
        start_x, start_y, _ = self.buffer[0]
        end_x, end_y, _ = self.buffer[-1]
        
        delta_x = end_x - start_x
        delta_y = end_y - start_y
        
        # Horizontal dominance and minimum distance
        if abs(delta_x) >= self.min_dist and abs(delta_x) > abs(delta_y) * 1.5:
            if delta_x < 0:
                return "LEFT", delta_x, delta_y
            else:
                return "RIGHT", delta_x, delta_y
                
        return None, delta_x, delta_y

    def clear(self):
        self.buffer.clear()

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

    # Configuration for Interaction
    click_threshold = 35       # pixel distance
    cooldown_time = 0.5        # seconds
    smooth_factor = 0.4        # higher means less smooth, more responsive
    scroll_sensitivity = 2     # multiplier for scroll delta
    
    # Back/Forward Gesture Tracker
    swipe_tracker = SwipeTracker(min_dist=120, max_time=0.7)
    back_cooldown = 1.5
    
    last_left_click_time = 0
    last_right_click_time = 0
    last_back_time = 0
    
    prev_x, prev_y = screen_w // 2, screen_h // 2
    prev_scroll_y = None
    
    print("Starting AirCursor System Gesture Control...")
    print("Press 'ESC' in the video window to exit.")

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            continue

        # Flip the image horizontally for a natural selfie-view behavior
        frame = cv2.flip(frame, 1)
        h, w, c = frame.shape
        
        # Define a centered interaction zone
        pad_x, pad_y = int(w * 0.15), int(h * 0.2)
        cv2.rectangle(frame, (pad_x, pad_y), (w - pad_x, h - pad_y), (255, 0, 255), 2)
        
        # Convert BGR image to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the image and find hands
        results = hands.process(rgb_frame)
        
        state_label = "Scanning..."
        state_color = (200, 200, 200)
        debug_text = ""

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                # Fetch Tips
                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
                
                # Fetch boolean UP states
                index_up = is_finger_up(index_tip, hand_landmarks.landmark[6])
                middle_up = is_finger_up(middle_tip, hand_landmarks.landmark[10])
                ring_up = is_finger_up(hand_landmarks.landmark[16], hand_landmarks.landmark[14])
                pinky_up = is_finger_up(hand_landmarks.landmark[20], hand_landmarks.landmark[18])
                
                fingers_up_count = sum([index_up, middle_up, ring_up, pinky_up])
                
                # Convert normalized coordinates to pixel
                ix, iy = int(index_tip.x * w), int(index_tip.y * h)
                tx, ty = int(thumb_tip.x * w), int(thumb_tip.y * h)
                mx, my = int(middle_tip.x * w), int(middle_tip.y * h)
                
                # Visual dots
                cv2.circle(frame, (ix, iy), 8, (255, 0, 0), cv2.FILLED)
                cv2.circle(frame, (tx, ty), 8, (0, 0, 255), cv2.FILLED)
                cv2.circle(frame, (mx, my), 8, (0, 255, 0), cv2.FILLED)
                
                # Distances for clicks
                dist_left_click = np.hypot(tx - ix, ty - iy)
                dist_right_click = np.hypot(tx - mx, ty - my)
                
                # Determine conflicting states to pause swipe tracking
                is_scrolling = index_up and middle_up and not ring_up and not pinky_up
                is_pinching = (dist_left_click < click_threshold) or (dist_right_click < click_threshold)
                
                swipe_dir = None
                dx, dy = 0, 0
                
                if fingers_up_count >= 3 and not is_scrolling and not is_pinching:
                    swipe_tracker.add_point(ix, iy)
                    swipe_dir, dx, dy = swipe_tracker.check_swipe()
                    debug_text = f"dx: {dx} dy: {dy}"
                else:
                    swipe_tracker.clear()
                
                # Mapping index finger to screen mapping
                mapped_x = np.interp(ix, (pad_x, w - pad_x), (0, screen_w))
                mapped_y = np.interp(iy, (pad_y, h - pad_y), (0, screen_h))
                
                # Priority Evaluator Block
                
                # 1. Pause Mode
                if index_up and middle_up and ring_up and pinky_up and not swipe_dir:
                    state_label = "Paused"
                    state_color = (0, 165, 255) # Orange
                    prev_scroll_y = None
                
                # 2. Back/Forward Gesture (Swipe)
                elif swipe_dir:
                    state_label = f"Swipe {swipe_dir} Detected"
                    state_color = (255, 105, 180) if swipe_dir == "LEFT" else (255, 165, 0)
                    prev_scroll_y = None
                    
                    current_time = time.time()
                    if current_time - last_back_time > back_cooldown:
                        if swipe_dir == "LEFT":
                            with open("gesture_command.txt", "w") as f:
                                f.write("HOME")
                            cv2.putText(frame, "BACK TRIGGERED", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
                        elif swipe_dir == "RIGHT":
                            with open("gesture_command.txt", "w") as f:
                                f.write("MENU")
                            cv2.putText(frame, "FORWARD TRIGGERED", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
                        
                        last_back_time = current_time
                        swipe_tracker.clear() # Reset buffer so it doesn't instantly double-trigger
                        
                # 3. Scroll
                elif is_scrolling:
                    state_label = "Scroll"
                    state_color = (255, 255, 0) # Cyan
                    
                    # Scroll logic based on average Y of index & middle
                    current_y = (iy + my) / 2
                    if prev_scroll_y is not None:
                        delta = current_y - prev_scroll_y
                        if abs(delta) > 5:  # Deadzone to prevent micro-jitters
                            pyautogui.scroll(int(-delta * scroll_sensitivity))
                    prev_scroll_y = current_y
                    
                # 4. Right Click
                elif dist_right_click < click_threshold:
                    state_label = "Right Click"
                    state_color = (255, 0, 255) # Magenta
                    prev_scroll_y = None
                    current_time = time.time()
                    if current_time - last_right_click_time > cooldown_time:
                        pyautogui.rightClick()
                        last_right_click_time = current_time
                        cv2.circle(frame, ((tx+mx)//2, (ty+my)//2), 20, (255, 0, 255), cv2.FILLED)
                        
                # 5. Left Click
                elif dist_left_click < click_threshold:
                    state_label = "Left Click"
                    state_color = (0, 255, 0) # Green
                    prev_scroll_y = None
                    current_time = time.time()
                    if current_time - last_left_click_time > cooldown_time:
                        pyautogui.click()
                        last_left_click_time = current_time
                        cv2.circle(frame, ((tx+ix)//2, (ty+iy)//2), 20, (0, 255, 0), cv2.FILLED)
                        
                # 6. Move
                else:
                    state_label = "Move"
                    state_color = (255, 0, 0) # Blue
                    prev_scroll_y = None
                    
                    # Apply smoothing to the cursor movement
                    curr_x = prev_x + (mapped_x - prev_x) * smooth_factor
                    curr_y = prev_y + (mapped_y - prev_y) * smooth_factor
                    
                    # Move the mouse cursor
                    try:
                        pyautogui.moveTo(curr_x, curr_y)
                    except Exception:
                        pass
                    
                    prev_x, prev_y = curr_x, curr_y

        # Display the active gesture on the screen
        cv2.putText(frame, f"State: {state_label}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, state_color, 3)
        if debug_text:
            cv2.putText(frame, debug_text, (20, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        cv2.imshow("Hand Tracking Gesture Control", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
