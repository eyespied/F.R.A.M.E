from gui import FrameGUI
from imutils.video import VideoStream
import time

print("[MSG] APPLICATION STARTING")
vs = VideoStream(src=0).start()
time.sleep(2.0)
app = FrameGUI(vs)
print("[MSG] APPLICATION LOADED")
app.root.mainloop()