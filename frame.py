__author__ = "James Clark, Hugo A'Violet, Sam Tredgett"
__copyright__ = "Copyright 2020, F.R.A.M.E Project"
__credits__ = ["James Clark", "Hugo A'Violet", "Sam Tredgett"]
__version__ = "1.0"

# Import in necessary libraries
from gui import FrameGUI
import gui
import systemtimer
from imutils.video import VideoStream
import time
import threading


# Start Web cam Video Stream
# src=0 - USB Web cam
# src=1 - Laptop In-built Web cam
print("[INFO] APPLICATION STARTING")
vs = VideoStream(src=0).start()
time.sleep(2.0)
app = FrameGUI(vs)
print("[INFO] APPLICATION LOADED")

# Starts thread for the late timer
set_thread = threading.Thread(target=gui.lateTimer)
set_thread.start()

# Starts thread for the system timer
system_thread = threading.Thread(target=systemtimer.systemTimer)
system_thread.start()

# Launches GUI Application
app.root.mainloop()
