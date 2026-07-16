# Hand Control
### ***WARNING: This project is still in development, there is no guarantee it will work until this notice is removed.***  
  A webcam-based hand control system for Linux desktops, written in Python. Tested with CachyOS + Niri.

## Dependencies
1) Python and PIP
   
       pacman -S python python-pip
3) MediaPipe and OpenCV  

       pip install mediapipe opencv-python
   *Note: Make sure you set up a Python virtual environment and use the* `source` *command to run from it. Otherwise, PIP will fail to install the necessary packages.*
5) Download the MediaPipe Hand Landmarker Task model.  
   *Note: The Hand Landmarker Task Model is currently included in the repo for testing purposes. It will be removed when base development is complete.*  

   Run the following from the folder you intend to use to store the .py file:

       curl -L -o hand_landmarker.task \ 
       https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task

## Installation and Running
1) Download `unified_hand_control.py` and `config.json` from the repo.
2) If not already, move both files to the same directory as the Hand Landmarker Task Model
   
        mv ~/Downloads/unified_hand_control.py /your/directory/here
        mv ~/Downloads/config.json /your/directory/here
3) Open a terminal at the same directory above and run the application with Python

        cd /your/directory/here/
        
        # On most DEs + configurations:
        python unified_hand_control.py
        
        # If you recieve a "no QT platform plugin could be initialized" error:
        QT_QPA_PLATFORM=xcb python unified_hand_control.py
   *To change any presets, edit the* `config.json` *file with your preferred text/json editor.*
