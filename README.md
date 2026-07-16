# Hand Control
  A webcam-based hand control system for Linux desktops, written in python.
  Tested with CachyOS + Niri.

## Dependencies
1) Python and PIP  
   `pacman -S python python-pip`
2) MediaPipe and OpenCV  
   `pip install mediapipe opencv-python`

   *Note: Make sure you set up a Python virtual environment and use the `source` command to run from it. Otherwise, PIP will fail to install the necessary packages.*
3) Download the MediaPipe Hand Landmarker Task model.  
   *Note: The Hand Landmarker Task Model is currently included in the repo for testing purposes. It will be removed when base development is complete.*  

   Run the following from the folder you intend to use to store the .py file:  
   `curl -L -o hand_landmarker.task \ https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task`
