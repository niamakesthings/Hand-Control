# IMPORTANT: For now, this project only supports Linux desktops
# I might see if I can expand it to Windows in the future; macOS is unlikely since:
#   a) I don't have a mac, and
#   b) I don't have the money to buy a mac.
# Everything here is tested in a CachyOS + Niri configuration, and generally should work without modifications
# on any linux system running a Niri DE.
# For other DEs, please edit the commands in config.json to whatever suits your use case.

# Also, the gestures may be finicky depending on the quality of your webcam, lighting, etc. My recommendation
# is to hold your palm out with all fingers extended, then practice a bit with just your index finger.
# You may also need to tweak the movement presets in config.json until they are to your liking.


import subprocess
import time
from collections import deque

import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

import json


# Landmark constants for ease of use: NOTE: DO NOT CHANGE!
LANDMARKS = {
    "wrist": 0,
    "thumb": 4,
    "index": 8,
    "middle": 12,
    "ring": 16,
    "pinky": 20,
}

def load_json(json_path: str):
    # Attempt to open and load data from config.json
    try:
        with open(json_path) as handler:
            return json.load(handler)

    except FileNotFoundError as e:
        print("Error: Application would not locate config.json file. Is it located in the same directory as the application file?")
        raise
    
    except PermissionError as e:
        print("Error: Application does not have read permissions for config.json. Consider using chmod?")
        raise

def init_landmarker(model_path: str):
    # Set up landmarker
    landmarker_options = vision.HandLandmarkerOptions(
        base_options=mp_python.BaseOptions(model_asset_path=model_path),
        running_mode=vision.RunningMode.VIDEO,
        num_hands=1
    )

    landmarker = vision.HandLandmarker.create_from_options(landmarker_options)
    return landmarker

def init_cam(webcam_index: int):
    # Set up camera capture
    cam = cv2.VideoCapture(webcam_index)
    if not cam.isOpened:
        raise RuntimeError("Could not open webcam at index " + WEBCAM_INDEX + ". Your webcam is at a different index? The appropriate drivers aren't installed?")
    return cam

def init_buffer(landmarks):
    # Set up history buffer and timestamp tracking NOTE: Right now the implementation is only for the index finger
    history = {}
    for key in landmarks.keys():
        history[key] = deque()
    
    return history

def get_results(frame, frame_index, landmarker):
    rgb_cvt = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_cvt)
    timestamp_ms = int(frame_index * 1000 / 30) # 1s = 1000ms, 30f = 1s
    results = landmarker.detect_for_video(mp_image, timestamp_ms)
    return results

def main() -> None:
    settings = load_json('config.json')


    # Initialize constants based on loaded data in "settings"
    try:
        WEBCAM_INDEX = settings["webcam"]["index"]
        SHOW_FEED = settings["webcam"]["show_feed"]
        MODEL_PATH = settings["model_path"]

        WINDOW_SECONDS = settings["evaluation"]["window_seconds"] # Amount of past time the program analyzes to detect a swipe
        COOLDOWN_SECONDS = settings["evaluation"]["cooldown_seconds"] # Minimum amount of time the program allows between swipes

        SWIPE_THRESHOLD_X = settings["movement"]["swipe_threshold_x"] # Minimum percentage of the screen a swipe needs to travel horizontally across to be registered.
        SWIPE_THRESHOLD_Y = settings["movement"]["swipe_threshold_y"] # Same as above, but vertically

        ACTIONS = settings["actions"] # Dictionary of all triggerable gestures and corresponding commands
    
    except KeyError as e:
        print("Error: Could not load settings from config.json. File may be malformed.")
        raise



    landmarker = init_landmarker(MODEL_PATH)
    cam = init_cam(WEBCAM_INDEX)

    history = init_buffer(LANDMARKS)
    last_trigger_time = 0.0
    frame_index = 0

    try:
        while True:
            active, frame = cam.read()
            if not active:
                break
            
            results = get_results(frame, frame_index, landmarker)
            frame_index += 1
            now = time.time()

            if results.hand_landmarks:
                positions = {}
                for key, landmark in LANDMARKS.items():
                    positions[key] = results.hand_landmarks[0][landmark] # [0] refers to the first hand catagorized. For now, there is only single hand support.
                    history[key].append((now, positions[key].x, positions[key].y))

                    while history[key] and now - history[key][0][0] > WINDOW_SECONDS:
                        history[key].popleft()
                
                if now - last_trigger_time > COOLDOWN_SECONDSS!!: # len(history) ensures there's at least 2 data points to extrapolate based off of.

                    deltas = {}
                    for key in positions.keys():
                        if len(history[key]) > 1:
                            _, x0, y0 = history[key][0]
                            _, x1, y1 = history[key][-1]
                            deltas[key] = (x1-x0, y1-y0)
                        else:
                            deltas[key] = (0, 0)
                    

                    # Total measure of the "influence" of each direction so that the largest may be chosen with respect to thresholds
                    x_ratio = abs(deltas["index"][0]) / SWIPE_THRESHOLD_X
                    y_ratio = abs(deltas["index"][1]) / SWIPE_THRESHOLD_Y

                    
                    if x_ratio >= 1.0 or y_ratio >= 1.0:
                        if x_ratio > y_ratio:
                            direction = "left" if deltas["index"][0] < 0 else "right"
                        else:
                            direction = "up" if deltas["index"][1] < 0 else "down"
                    
                        result = subprocess.run(ACTIONS["swipe"]["one_finger"][direction].split())
                        last_trigger_time = now
                        history["index"].clear()

            else:
                for key in history.keys():
                    history[key].clear()

            if SHOW_FEED:
                cv2.imshow("Debug Panel", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

    
    finally:
        cam.release()
        cv2.destroyAllWindows()




if __name__ == "__main__":
    main()


