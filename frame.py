from gui import FrameGUI
from imutils.video import VideoStream
import time

print("[INFO] APPLICATION STARTING")
vs = VideoStream(src=1).start()
time.sleep(2.0)
app = FrameGUI(vs)
print("[INFO] APPLICATION LOADED")
app.root.mainloop()