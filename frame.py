__author__ = "James Clark"
__copyright__ = "Copyright 2020, F.R.A.M.E Project"
__credits__ = ["James Clark"]
__version__ = "1.0"

# Import in necessary libraries
from gui import FrameGUI
import gui
import systemtimer
from imutils.video import VideoStream
import time
import threading

# Sets global variable, ifClass checks sets a current class in progress to True or False
ifClass = False


# If class isn't in progress creates a thread and calls classCheck function
def classCheck_():
    global ifClass
    class_check = threading.Thread(target=systemtimer.classCheck)
    class_check.start()


exec(open('scripts/splashscreen.py').read())

# Start Web cam Video Stream
# src=0 - USB Web cam
# src=1 - Laptop In-built Web cam
gui.machineCode()
print("[INFO] F.R.A.M.E BOOTING")
vs = VideoStream(src=0).start()

time.sleep(1)
app = FrameGUI(vs)

if not ifClass:
    ifClass = True
    classCheck_()

# Launches GUI Application
app.root.mainloop()
