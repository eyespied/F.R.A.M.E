__author__ = "James Clark, Hugo A'Violet, Sam Tredgett"
__copyright__ = "Copyright 2020, F.R.A.M.E Project"
__credits__ = ["James Clark", "Hugo A'Violet", "Sam Tredgett"]
__version__ = "1.0"

# TODO:
#   - Check threading, end a thread if not needed.
#   - Export out of one-drive check speeds
#   - Clean up code / redundant code
#   - Comment all code so its up to date
#   - custom video filter?

# Import in necessary libraries
from gui import FrameGUI
import systemtimer
from imutils.video import VideoStream
import time
import threading

ifClass = False


def classCheck_():
    global ifClass
    class_check = threading.Thread(target=systemtimer.classCheck)
    class_check.start()


# Start Web cam Video Stream
# src=0 - USB Web cam
# src=1 - Laptop In-built Web cam
print("[INFO] APPLICATION STARTING")
vs = VideoStream(src=0).start()

time.sleep(1)
app = FrameGUI(vs)
print("[INFO] APPLICATION LOADED")

if not ifClass:
    ifClass = True
    classCheck_()

# Launches GUI Application
app.root.mainloop()
