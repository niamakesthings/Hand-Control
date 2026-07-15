# IMPORTANT: For now, this project only supports Linux desktops
# I might see if I can expand it to windows in the future; macOS is unlikely since:
#   a) I don't have a mac, and
#   b) I don't have the money to buy a mac.
# Everything here is tested in a CachyOS + Niri configuration, and generally should work without modifications
# on any linux system running a Niri DE.
# For other DEs, please edit the commands in the ACTIONS dictionary to whatever suits your use case.

# Also, the gestures may be finicky depending on the quality of your webcam, lighting, 

import subprocess
import time
from collections import deque

import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

# Model path: Change this if using a custom model
MODEL_PATH = "hand_landmarker.task"
 
# Evaluation constants
WINDOW_SECONDS = 0.15 # How recent a movement must be to be considered for a swipe
COOLDOWN_SECONDS = 0.25 # Minimum triggering time between swipes

# Movement thresholds
# NOTE: This may be deprecated in a future commit for a 4-axis system (up/down/left/right)
SWIPE_THRESHOLD_X = 0.10
SWIPE_THRESHOLD_Y = 0.18

# Landmark constants for ease of use: DO NOT CHANGE!
WRIST_LANDMARK = 0
THUMB_LANDMARK = 4
INDEX_LANDMARK = 8
MIDDLE_LANDMARK = 12
RING_LANDMARK = 16
PINKY_LANDMARK = 20

# Dictionary of all gesture actions and corresponding commands. sorted() ensures that the right order is used every time
# Format for actions is denoted as finger_direction
# HACK: This dictionary is maybe on of the ugliest pieces of code I have ever written and will probably be changed later.
ACTIONS = {
    #sorted(["ACTIONS", "GO", "HERE"]): ["COMMAND", "GOES", "HERE"],\
    sorted(["index_down"], "niri msg action focus-workspace-down".split())
    sorted(["index_up"], "niri msg action focus-workspace-up".split())

}


