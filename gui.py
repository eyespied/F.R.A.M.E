__author__ = "James Clark, Hugo A'Violet, Sam Tredgett"
__copyright__ = "Copyright 2020, F.R.A.M.E Project"
__credits__ = ["James Clark", "Hugo A'Violet", "Sam Tredgett"]
__version__ = "1.0"

# Import in necessary libraries
import tkinter as tk
import threading
import cv2
import face_recognition
from PIL import Image, ImageTk
import datetime
import os
import sqlForGui
import time


# Exception to Breakout of For Loop
class BreakIt(Exception): pass


# Stores attended UserID's in a list
attendees = []
# Stores late attended UserID's in a list
late_attendees = []


# lateTimer that activates when late_timer reaches 0

def lateTimer():
    global isLate
    global late_timer

    # Late timer variable (seconds) change this to change the timer.
    late_timer = 10
    while late_timer > 0:
        isLate = False
        time.sleep(1)
        late_timer -= 1

    isLate = True
    if isLate:
        print("[INFO] USERS WILL NOW BE MARKED AS LATE")


# Adds Users to Attended List
# If isLate is True add the attended to the late list also
def addUserToAttendList(userid):
    attendees.append(userid)
    print("[INFO] ADDED USER TO ATTENDANCE LIST")
    if isLate:
        late_attendees.append(userid)
        print("[INFO] ADDED USER TO LATE-ATTENDANCE LIST")


# Updates GUI with a tick if user is found in the system
# @param userid - The User's ID
# @param timestamp - Filename of photo without the extension
def updateGUIYes(userid, timestamp):
    print("[SQL] UPDATED GUI WITH DETAILS")
    # Calls DB to pull the userID, First Name and Last Name
    sqlForGui.readUserData(userid)

    tick = tk.PhotoImage(file="images/tick.png")
    found = tk.Label(FrameGUI.root, compound=tk.CENTER, image=tick, bg='#05345C')
    found.image = tick
    found.place(relx=0.249, rely=0.15, relwidth=0.5, relheight=0.4)
    # Removes GUI tick after 3 seconds
    found.after(3000, lambda: found.place_forget())

    # Prints out the User's Information
    userInformation = """{}\n{} {}""".format(sqlForGui.user, sqlForGui.fname, sqlForGui.lname)
    user = tk.Label(FrameGUI.root, text=userInformation, font=30)
    user.place(relx=0.249, rely=0.55, relwidth=0.5, relheight=0.2)
    # Removes User Information after 3 seconds
    user.after(3000, lambda: user.place_forget())

    # Calls add User function
    addUserToAttendList(userid)
    # Updates DB with the timestamp the photo was taken
    sqlForGui.updateTimeStamp(userid, timestamp)


# Updates GUI with a cross if no face found
def updateGUINo():
    print("[INFO] UPDATED GUI WITH DETAILS")

    cross = tk.PhotoImage(file="images/cross.png")
    found = tk.Label(FrameGUI.root, compound=tk.CENTER, image=cross, bg='#05345C')
    found.image = cross
    found.place(relx=0.249, rely=0.15, relwidth=0.5, relheight=0.4)
    found.after(3000, lambda: found.place_forget())

    userInformation = "Error: Try Again"
    user = tk.Label(FrameGUI.root, text=userInformation, font=30)
    user.place(relx=0.249, rely=0.55, relwidth=0.5, relheight=0.2)
    user.after(3000, lambda: user.place_forget())


# Computes facial recognition
# @param filename - photo take was taken
def computeImage(filename):
    print("[INFO] CROSS-REFERENCING IMAGE")

    # Directory of cross-referenced photos
    directory = "output/"
    file_names = os.listdir(directory)

    # Stores the current photo taken
    picture_of_me = face_recognition.load_image_file("rawimages/{}".format(filename))

    try:
        my_face_encoding = face_recognition.face_encodings(picture_of_me)[0]
        print("[INFO] CHECKING IF USER IS IN DATABASE")
        try:
            # For every file in the directory check if the current photo matches any of their face encodings
            for i in file_names:
                iPath = os.path.join(directory, i)
                with open(iPath, 'rb') as fh:

                    new_picture = face_recognition.load_image_file(iPath)

                    for face_encoding in face_recognition.face_encodings(new_picture):

                        results = face_recognition.compare_faces([my_face_encoding], face_encoding)

                        # If found, convert filename to a timestamp
                        # Call UpdateGUI Yes function, passing in the userID and timestamp
                        if results[0]:
                            userID = ''.join(filter(lambda x: x.isdigit(), iPath))
                            print("[INFO] USER FOUND | ID : {}".format(userID))
                            timestamp = (filename.rsplit(".", 1)[0])
                            updateGUIYes(userID, timestamp)

                            # Break out of For Each Loop
                            raise BreakIt
                        else:
                            pass
        except BreakIt:
            pass

    # If no face found in photo UpdateGUI with No
    except IndexError as e:
        updateGUINo()
        print("[INFO] NO USERS FOUND")


# Class that deals with the GUI

class FrameGUI:
    root = None

    def __init__(self, vs):
        # Output path of photos taken
        self.outputPath = 'rawimages'
        self.vs = vs
        self.frame = None
        self.thread = None
        self.stopEvent = None
        # Initialize root window
        self.root = tk.Tk()
        self.panel = None
        self.userID = None

        # Parameters to store int values for size of window
        CANVAS_HEIGHT = 720
        CANVAS_WIDTH = 1280

        # Window information
        self.root.iconbitmap('images/favicon.ico')
        self.root.title("F.R.A.M.E - Facial Recognition Attendance Monitoring Engine")

        # Creates canvas, which is a child of root and sets the size of the window
        canvas = tk.Canvas(self.root, height=CANVAS_HEIGHT, width=CANVAS_WIDTH, bg='#05345C')
        canvas.pack()

        # Creates a frame for the button at the lower half of the Canvas window
        self.buttonFrame = tk.Frame(self.root, bg='#b3e6ff')
        self.buttonFrame.place(relx=0.5, rely=0.8, relwidth=0.75, relheight=0.1, anchor='n')

        # Take Photo Button that uses an image
        self.buttonImage = Image.open('images/button.png')
        self.buttonImageCopy = self.buttonImage.copy()
        self.photo = ImageTk.PhotoImage(self.buttonImage)
        self.button = tk.Button(self.buttonFrame, image=self.photo, bg='#05345C', highlightcolor='#05345C',
                                activebackground='#003882', command=self.takeImage)
        # button.bind('<Configure>', resizeImages.resize_image())
        self.button.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Creates a frame for the title of our project 'F.R.A.M.E'
        self.titleFrame = tk.Frame(self.root, bg='#05345C')
        self.titleFrame.place(relx=0.5, rely=0, relwidth=1, relheight=0.1, anchor='n')

        # Title Frame that uses an image
        self.titleImage = Image.open('images/title.png')
        self.titleImageCopy = self.titleImage.copy()
        self.photo2 = ImageTk.PhotoImage(self.titleImage)
        self.title = tk.Label(self.titleFrame, image=self.photo2, bg='#05345C')
        # title.bind('<Configure>', resizeImages.resize_image2)
        self.title.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Background Image
        self.background_image = Image.open('images/bg.png')
        self.background_imageCopy = self.background_image.copy()
        self.photo3 = ImageTk.PhotoImage(self.background_image)
        self.background_label = tk.Label(canvas, image=self.photo3)
        # background_label.bind('<Configure>', resizeImages.resize_image3)
        self.background_label.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Create Frame for How to Use
        self.howToUseFrame = tk.Frame(self.root, bg='#05345C')
        self.howToUseFrame.place(relx=1, rely=1, relwidth=0.08, relheight=0.1, anchor='se')

        # How to Use Button
        self.howToUseButton = Image.open('images/howtouse.png')
        self.howToUseButton_Copy = self.howToUseButton.copy()
        self.photo4 = ImageTk.PhotoImage(self.howToUseButton)
        self.button2 = tk.Button(self.howToUseFrame, image=self.photo4, bg='#05345C', highlightcolor='#05345C',
                                 activebackground='#003882')
        # button2.bind('<Configure>', resizeImages.resize_image4)
        self.button2.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.stopEvent = threading.Event()
        self.thread = threading.Thread(target=self.videoLoop, args=())
        self.thread.start()

        self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)

    # Creates a video loop frame in the center of the GUI
    def videoLoop(self):
        try:
            while not self.stopEvent.is_set():
                self.frame = self.vs.read()

                image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(image)
                image = ImageTk.PhotoImage(image)

                if self.panel is None:
                    # Create Frame for Video
                    self.panel = tk.Label(image=image)
                    self.panel.image = image
                    self.panel.place(relx=0.249, rely=0.15, relwidth=0.5, relheight=0.6)

                else:
                    self.panel.configure(image=image)
                    self.panel.image = image

        except RuntimeError as e:
            print("[INFO] RUNTIME ERROR CATCH")

    # Takes Image Function
    # Stores timestamp and filename
    def takeImage(self):
        timestamp = datetime.datetime.now()
        filename = "{}.jpg".format(timestamp.strftime("%Y-%m-%d_%H-%M-%S"))
        p = os.path.sep.join((self.outputPath, filename))
        # Save file
        cv2.imwrite(p, self.frame.copy())
        print("[INFO] PHOTO SAVED TO OUTPUT DIR at", timestamp)
        # Calls facial recognition function
        computeImage(filename)

    # Closes application when X is clicked
    def onClose(self):
        print("[INFO] APPLICATION CLOSING")
        self.stopEvent.set()
        self.vs.stop()
        self.root.quit()
