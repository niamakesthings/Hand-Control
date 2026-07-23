# GitHub: https://github.com/niamakesthings/Hand-Control


import platform
import sys
import subprocess
import os
import time
from collections import deque
from pathlib import Path
import urllib.request as request

import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

import json

JSON_EXTENSION = "config.json"
DEFAULT_MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"

PLATFORM = platform.system()

# Default json settings for creating initial json file, if required. Else, unused.
# NOTE: Do not edit these values. Edit config.json instead. 
DEFAULT_SETTINGS = {
    "execution_tool": "",
    "debug_mode": False,
    "webcam": {
        "index": 0,
        "show_feed": True
    },
    "model_path": "hand_landmarker.task",
    "evaluation": {
        "window_seconds": 0.15,
        "cooldown_seconds": 0.25
    },
    "movement": {
        "swipe_threshold_x": 0.1,
        "swipe_threshold_y": 0.18
    },
    "proximity": {
        "require_proximity": False,
        "proximity_threshold": 0.2
    },
    "actions": {
        "swipe": {
            "one_finger": {
                "up": "",
                "down": "",
                "left": "",
                "right": ""
            },
            "two_finger": {
                "up": "",
                "down": "",
                "left": "",
                "right": ""
            },
            "three_finger": {
                "up": "",
                "down": "",
                "left": "",
                "right": ""
            }
        }
    }
}

# Landmark constants for ease of use: NOTE: DO NOT CHANGE!
LANDMARKS = {
    "wrist": 0,
    "thumb": 4,
    "index": 8,
    "middle": 12,
    "ring": 16,
    "pinky": 20,
}

def setup():
    # For stability: resolves the base directory and changes the config.json path accordingly
    resolve_base_dir()
    global JSON_PATH
    JSON_PATH = str(Path(BASE_DIR) / JSON_EXTENSION)

    # Confirm config.json exists at JSON_PATH, and create it if not
    resolve_config(JSON_PATH, DEFAULT_SETTINGS)
    
    # Load all initialization and execution constants from config.json as global variables
    load_constants_from_config(JSON_PATH)

    # Confirm hand_landmarker.task exists, and download it if not
    resolve_model(MODEL_PATH, DEFAULT_MODEL_URL)

    # Select the execution tool, or prompt the user to set one up if none selected
    select_exec_tool(EXEC_TOOL, PLATFORM)


def resolve_config(json_path: str, default_settings: dict):
    if Path(json_path).exists():
        print("Existing config.json file found. Using config settings.")
    else:
        print("No existing config.json could be found. Creating new file...")
        if input("A new config file is being created. Would you like a guided customization? [y/N]: ").lower() == "y":
            print("NOTICE: Guided customization is currently in progress and scheduled for a future version!\nIn the meantime, please edit config.json directly.")
        else:
            print("Guided customization skipped. Using default settings.")

        with open(json_path, "w", encoding="utf-8") as file:
            json.dump(default_settings, file, indent=4)

def resolve_model(model_path: str, model_url: str):
    if Path(model_path).exists():
        print(f"Existing {model_path} found. Using file.")
    else:
        print("No existing .task file could be found. It may not be dowloaded or placed in the correct directory.")
        if input("Download a new hand_landmarker.task file? This may take a couple minutes depending on your WiFi speed. [Y/n]: ").lower() != "n":
            try:
                print("Downloading new model...")
                request.urlretrieve(model_url, model_path)
                print("Model download successful!")
            except Exception:
                print("Error downloading the model. Please review the error message below.")
                raise

def resolve_base_dir():
    global BASE_DIR
    
    if getattr(sys, "frozen", False):
        BASE_DIR = os.path.dirname(sys.executable)
    else:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def select_exec_tool(exec_tool: str, platform: str):
    if exec_tool == "":
        set_tool = input("Your execution tool is unset.\nAn execution tool is required to run keyboard shortcuts and commands.\nWould you like to set one? [Y/n]: ")
        if set_tool.lower() != "n":
            option = int(input("\n Welcome to the execution tool selector. Please select from the following options:\n"+
                  "\t1) auto (choose the best tool for me automatically)\n"+
                  "\t2) pyautogui (effective on Windows, macOS, and Linux + X11/Xorg)\n"+
                  "\t3) ydotool (effective on all Linux devices)\n"+
                  "\t4) wayland-automation (effective on Linux + Wayland for specific compositors supporting wtype)\n"+
                  "\t5) command (executes a specified command in your terminal; WARNING: this will execute WHATEVER you write!)\n"+
                  "Execution Tool Number (default: 1) [1-4]: "))
        
            # If you're thinking the only reason I used a match/case here was that I just thought it'd be fun... you're right.
            match option:
                case 2:
                    init_exec_tool("pyautogui", platform)
                    query_set_default_exec_tool(JSON_PATH, "pyautogui")
                case 3:
                    init_exec_tool("ydotool", platform)
                    query_set_default_exec_tool(JSON_PATH, "ydotool")
                case 4:
                    print("'wayland-automation' option is currently in development, and may be removed in favor of the 'ydotool' option.")
                    if input("Continue with the 'ydotool' option? [Y/n]: ").lower() != "n":
                        init_exec_tool("ydotool", platform)
                        query_set_default_exec_tool(JSON_PATH, "ydotool")
                case 5:
                    print("\nI trust you've read the parenthetical above. This option will run any command specified, including those which may be harmful.\n"+
                          "Be smart when using this setting: don't enter any commands you don't understand.\n"+
                          "If you're not sure WHY you need this option, it's best to try the other options instead.\n")
                    cont = input("Would you like to continue with the 'command' execution tool? [y/N]: ")
                    if cont.lower() == "y":
                        init_exec_tool("command", platform)
                        print("Please review your config.json's 'actions' section.\n")
                        query_set_default_exec_tool(JSON_PATH, "command")
                case _:
                    selection = exec_tool_auto_select(platform)
                    init_exec_tool(selection, platform)
                    query_set_default_exec_tool(JSON_PATH, selection)


def exec_tool_auto_select(platform: str) -> str:
    print(platform + " platform detected.")
    if platform in ["Windows", "Darwin"]:
        print("'pyautogui' option has been selected!")
        return "pyautogui"

    elif platform in ["Linux"]:
        if os.environ.get("XDG_SESSION_TYPE") == "wayland":
            print("Wayland server detected.")
            print("'ydotool' option has been selected!")
            return "ydotool"
        else:
            print("X11/Xorg server detected.")
            print("'pyautogui' option has been selected!")
            return "pyautogui"
    else:
        print("Unable to identify platform.")
        print("Defaulting to option 'pyautogui'.")
        return "pyautogui"
    

def init_exec_tool(exec_tool: str, platform: str):
    print(f"Testing option '{exec_tool}'...")

    if exec_tool == "pyautogui":
        try:
            import pyautogui
        except ModuleNotFoundError:
            print("Module 'pyautogui' could not be imported. Please ensure it is installed via pip.")
            raise
        except FileNotFoundError:
            print("1 or more files associated with 'pyautogui' module could not be found. Please review the error.\nIf the problem persists, try 'ydotool' option instead.")
            raise
    
    elif exec_tool == "ydotool":
        if platform == "Linux":
            import shutil
            import subprocess

            if shutil.which("ydotool") is not None:
                print("'ydotool' binary detected.")
            else:
                print("'ydotool' binary could not be found. Please ensure it is properly installed.")
                raise RuntimeError
            
            try:
                if "running" in subprocess.run("systemctl --user status ydotool".split(), capture_output=True, text=True).stdout.strip():
                    print("'ydotool' daemon active.")
                else:
                    print("'ydotool' daemon could not be detected. Please ensure it is being run.")
                    print("NOTICE: Due to the ydotool daemon behaving differently across different distros, there is an override option available.\nPlease do not override unless you have verified yourself that the daemon is running.")
                    override = input("Override? [y/N]: ")
                    if override.lower() != "y":
                        raise RuntimeError
            except (FileNotFoundError, subprocess.SubprocessError):
                print("Could not check for 'ydotool'. If not using systemd, this is expected. If not, 'ydotool' may be installed in a nonstandard location.\n"+
                    "If you are confident that you installed 'ydotool' correctly, you should override this warning.")
                override = input("Override? [y/N]: ")
                if override.lower() != "y":
                    raise
        else:
            print("'ydotool' is currently only available on Linux devices. Please select another execution tool.")
            raise RuntimeError

    elif exec_tool == "command":
        import subprocess

        try:
            if subprocess.run([sys.executable, "-c", "print('commands-active')"], capture_output=True, text=True).stdout.strip() == "commands-active":
                print("'command' option operational via 'subprocess' module.")
            else:
                print("'command' option via 'subprocess' module failed to execute correctly. Command ran without error, but results did not match expected returns.")
                raise RuntimeError
        
        except subprocess.SubprocessError:
            print("'command' option via 'subprocess' module failed to execute. Command did not run.")
            raise
    
    print(f"Success! Option '{exec_tool}' has been set.")


def query_set_default_exec_tool(json_path: str, exec_tool: str):
    keep = input(f"Would you like to set '{exec_tool}' as your default execution tool? You will not have to go through this configuration again. [Y/n]: ")
    if keep.lower() != "n":
        with open(json_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        data["execution_tool"] = exec_tool

        with open(json_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
        
        EXEC_TOOL = settings["execution_tool"]


def load_constants_from_config(json_path: str):
    global EXEC_TOOL, DEBUG_MODE, WEBCAM_INDEX, SHOW_FEED, MODEL_PATH, WINDOW_SECONDS, COOLDOWN_SECONDS, SWIPE_THRESHOLD_X, SWIPE_THRESHOLD_Y, ACTIONS

    try:
        with open(json_path, "r") as file:
            settings = json.load(file)

        EXEC_TOOL = settings["execution_tool"]
        
        DEBUG_MODE = settings["debug_mode"]

        WEBCAM_INDEX = settings["webcam"]["index"]
        SHOW_FEED = settings["webcam"]["show_feed"]
        MODEL_PATH = str(Path(BASE_DIR) / settings["model_path"])

        WINDOW_SECONDS = settings["evaluation"]["window_seconds"] # Amount of past time the program analyzes to detect a swipe
        COOLDOWN_SECONDS = settings["evaluation"]["cooldown_seconds"] # Minimum amount of time the program allows between swipes

        SWIPE_THRESHOLD_X = settings["movement"]["swipe_threshold_x"] # Minimum percentage of the screen a swipe needs to travel horizontally across to be registered.
        SWIPE_THRESHOLD_Y = settings["movement"]["swipe_threshold_y"] # Same as above, but vertically

        ACTIONS = settings["actions"] # Dictionary of all triggerable gestures and corresponding commands

    except FileNotFoundError:
        print("Error: Application would not locate config.json file. Is it located in the same directory as the application file?")
        raise
    
    except PermissionError:
        print("Error: Application does not have read permissions for config.json. Consider using chmod?")
        raise

    except KeyError:
        print("Error: Could not load settings from config.json. File may be malformed.")
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

    landmarker = init_landmarker(MODEL_PATH)
    cam = init_cam(WEBCAM_INDEX)

    if DEBUG_MODE: print("Model and Webcam initializations successful, now initializing history buffer.")

    history = init_buffer(LANDMARKS)
    last_trigger_time = 0.0
    frame_index = 0

    if DEBUG_MODE: print("History buffer initialization successful. Now beginning main loop.")

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
                    #TODO: positions is a redundant dictionary and all its functionality is captured by history. Remove after z values are properly implemented. Consider combining deltas into history as well.
                    positions[key] = results.hand_landmarks[0][landmark] # [0] refers to the first hand catagorized. For now, there is only single hand support.
                    history[key].append((now, positions[key].x, positions[key].y))

                    while history[key] and now - history[key][0][0] > WINDOW_SECONDS:
                        history[key].popleft()
                    
                    if DEBUG_MODE: print(key + " positions:\nx: " + str(history[key][-1][1]) + ", y: " + str(history[key][-1][2]) + ", z: " + (str(positions[key].z) if key != "wrist" else "N/A"))
                
                

                if now - last_trigger_time > COOLDOWN_SECONDS: #

                    deltas = {}
                    for key in positions.keys():
                        if len(history[key]) > 1:
                            _, x0, y0 = history[key][0]
                            _, x1, y1 = history[key][-1]
                            deltas[key] = (x1-x0, y1-y0)
                        else:
                            deltas[key] = (0, 0)
                    
                    for key in deltas.keys():
                        # Total measure of the "influence" of each direction so that the largest may be chosen with respect to thresholds
                        x_ratio = abs(deltas[key][0]) / SWIPE_THRESHOLD_X
                        y_ratio = abs(deltas[key][1]) / SWIPE_THRESHOLD_Y

                        
                        if x_ratio >= 1.0 or y_ratio >= 1.0:
                            if x_ratio > y_ratio:
                                direction = "left" if deltas[key][0] < 0 else "right"
                            else:
                                direction = "up" if deltas[key][1] < 0 else "down"
                        
                            #HACK
                            try:
                                result = subprocess.run(ACTIONS["swipe"]["one_finger"][direction].split())
                            except IndexError:
                                print("No Command")

                            last_trigger_time = now
                            history[key].clear()

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
    setup()
    main()
