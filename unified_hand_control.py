# IMPORTANT: For now, this project only supports Linux desktops
# I might see if I can expand it to windows in the future; macOS is unlikely since:
#   a) I don't have a mac, and
#   b) I don't have the money to buy a mac.
# Everything here is tested in a CachyOS + Niri configuration, and generally should work without modifications
# on any linux system running a Niri DE.
# For other DEs, please edit the commands in the ACTIONS dictionary to whatever suits your use case.

# Also, the gestures may be finicky depending on the quality of your webcam, lighting, etc. My recommendation
# is to hold your palm out with all fingers extended, then practice a bit with just your index finger.
# You may also need to tweak the presets in config.json until they are to your liking.


import subprocess
import time
from collections import deque

import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

import json


# Landmark constants for ease of use: NOTE: DO NOT CHANGE!
WRIST_LANDMARK = 0
THUMB_LANDMARK = 4
INDEX_LANDMARK = 8
MIDDLE_LANDMARK = 12
RING_LANDMARK = 16
PINKY_LANDMARK = 20


#NOTE: All following constants are now handled by the load_preferences() function and config.json file.
# Model path: Change this if using a custom model
MODEL_PATH = None

# Evaluation constants
WINDOW_SECONDS = None # How recent a movement must be to be considered for a swipe
COOLDOWN_SECONDS = None # Minimum triggering time between swipes

# Movement thresholds
# NOTE: This may be deprecated in a future commit for a 4-axis system (up/down/left/right)
SWIPE_THRESHOLD_X = None
SWIPE_THRESHOLD_Y = None



# Dictionary of all gesture actions and corresponding commands. sorted() ensures that the right order is used every time
# Format for actions is finger_direction
# HACK: This dictionary is maybe one of the ugliest pieces of code I have ever written and will probably be changed later.
ACTIONS = {
    #sorted(["ACTIONS", "GO", "HERE"]): ["COMMAND", "GOES", "HERE"],\
    sorted(["index_down"], "niri msg action focus-workspace-down".split())
    sorted(["index_up"], "niri msg action focus-workspace-up".split())

}

def load_preferences(json_path: str){
    try:
        with open(json_path) as handler:
            prefs = json.load(handler)

        MODEL_PATH = prefs["model_path"]

        WINDOW_SECONDS = prefs["evaluation"]["window_seconds"]
        COOLDOWN_SECONDS = prefs["evaluation"]["cooldown_seconds"]

        SWIPE_THRESHOLD_X = prefs["movement"]["swipe_threshold_x"]
        SWIPE_THRESHOLD_Y = prefs["movement"]["swipe_threshold_y"]
    
    except FileNotFoundError:
        print("Error: Application could not locate config.json file.")
    
    except PermissionError:
        print("Error: Application does not have read permissions for config.json")
}

def run_action():


def process_movement():

def handle_feed(show: bool, frame):
    if show:
        cv2.imshow("Hand Control Preview", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break


if __name__ == "__main__":


