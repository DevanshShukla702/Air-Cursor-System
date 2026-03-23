# AirCursor System

A gesture-controlled system that allows users to interact with a computer interface without touching any physical surface. The system uses a webcam to detect hand movements and convert them into mouse actions (cursor movement and click).

## Features
- **Real-time Hand Tracking**: Uses MediaPipe to track the index and thumb fingers.
- **Gesture Control**: Move your index finger to control the cursor, and pinch your thumb and index together to click.
- **Kiosk Interface**: A full-screen Streamlit application with large gesture-friendly buttons.

## Setup Requirements
Python 3.8+ is recommended. 
Ensure your environment grants camera permissions and accessibility permissions (required for PyAutoGUI to physically move the mouse on Mac/Windows).

### Installation
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Project
The project uses two components running simultaneously: the gesture control script running in the background, and the Streamlit UI running in the foreground.

**Step 1: Start the Gesture Control**
In one terminal, start the background gesture tracker:
```bash
python gesture_control.py
```
*Note: Depending on your system, you may need to allow accessibility/camera permissions for your terminal or IDE.*

**Step 2: Start the Kiosk UI**
In a separate terminal, launch the kiosk interface:
```bash
streamlit run app.py
```
This will open the interface in your web browser. You can now use your hand gestures to interact with the kiosk.
