__author__ = "James Clark, Hugo A'Violet, Sam Tredgett"
__copyright__ = "Copyright 2020, F.R.A.M.E Project"
__credits__ = ["James Clark", "Hugo A'Violet", "Sam Tredgett"]
__version__ = "1.0"

# Import in necessary libraries
import signal
import tkinter as tk
import threading
from tkinter import messagebox

import cv2
import face_recognition
from PIL import Image, ImageTk
import datetime
import os
import sqlForGui
import systemtimer


# Exception to Breakout of For Loop
class BreakIt(Exception):
    pass


# Stores attended UserID's in a list
attendees = []
# Stores late attended UserID's in a list
late_attendees = []
yes = False
possibleRooms = ["Room_001", "Room_002", "Room_003"]
finalRoomNumber = str(possibleRooms[0])
converted_module_code = ''
outputPath = "face_database/Photos_Taken/"


# Adds Users to Attended List
# If isLate is True add the attended to the late list also
def addUserToAttendList(userid):
    attendees.append(userid)
    print("[INFO] ADDED USER TO ATTENDANCE LIST")
    if systemtimer.isLate:
        late_attendees.append(userid)
        print("[INFO] ADDED USER TO LATE-ATTENDANCE LIST")


def updateGUIClassDetails():
    global converted_module_code
    print("[GUI] CLASS DETAILS PRINTED TO WINDOW")
    converted_module_code = sqlForGui.module_code
    updateFilePath()
    classDetails = [str(sqlForGui.module_code), sqlForGui.classDate, sqlForGui.classDescription,
                    sqlForGui.classLecturer,
                    sqlForGui.classLength]

    classLength = (sqlForGui.classLength / 60)

    classDetailsText = str(sqlForGui.classDate) + "\n\n" + str(sqlForGui.module_code) + "\n\n" + str(
        sqlForGui.classDescription) + "\n" \
                       + str(classLength) + " Hour(s)" + "\n\n" + str(sqlForGui.classLecturer)

    print(classDetails)
    classDetails = tk.Label(FrameGUI.root, text=classDetailsText, font=30)
    classDetails.place(relx=0.77, rely=0.15, relwidth=0.2, relheight=0.3)
    classDetails.after((sqlForGui.classLength * 1000), lambda: classDetails.place_forget())


def updateFilePath():
    global outputPath
    outputPath += converted_module_code


# Updates GUI with a tick if user is found in the system
# @param userid - The User's ID
# @param timestamp - Filename of photo without the extension
def updateGUIYes(userid, timestamp):
    print("[SQL] UPDATED GUI WITH DETAILS")
    # Calls DB to pull the userID, First Name and Last Name
    sqlForGui.readUserData(userid)

    if not systemtimer.isLate:
        tick = tk.PhotoImage(file="images/tick.png")
        found = tk.Label(FrameGUI.root, compound=tk.CENTER, image=tick, bg='#05345C')
        found.image = tick
        found.place(relx=0.249, rely=0.15, relwidth=0.5, relheight=0.4)
        # Removes GUI tick after 3 seconds
        found.after(3000, lambda: found.place_forget())

    if systemtimer.isLate:
        tick = tk.PhotoImage(file="images/late.png")
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
    directory = "face_database/Recognized_Faces/" + converted_module_code
    file_names = os.listdir(directory)

    # Stores the current photo taken
    picture_of_me = face_recognition.load_image_file(
        "face_database/Photos_Taken/" + converted_module_code + "/" + filename)

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
                            userID = userID[3:]
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


class FrameGUI:
    root = None

    def __init__(self, vs):
        # Output path of photos taken
        global outputPath
        self.vs = vs
        self.frame = None
        self.thread = None
        self.stopEvent = None
        # Initialize root window
        self.root = tk.Tk()
        self.panel = None
        self.userID = None
        self.emptyMenu = None
        self.roomNumber = tk.StringVar()
        self.selectRoomLab = None
        self.submitButton = None
        self.cancelButton = None
        self.roomEntered = None
        self.invalidRoom = None
        self.submittedValue = ''

        # Buttons for Select Room
        self.textMessageBox = None
        self.one_button = None
        self.two_button = None
        self.three_button = None
        self.four_button = None
        self.five_button = None
        self.six_button = None
        self.seven_button = None
        self.eight_button = None
        self.nine_button = None
        self.ten_button = None
        self.roomText = None

        # How to use
        self.howToUseLab = None
        self.howToUseButton = None

        # Parameters to store int values for size of window
        CANVAS_HEIGHT = 740
        CANVAS_WIDTH = 1280

        # Window information
        self.root.iconbitmap('images/favicon.ico')
        self.root.title("F.R.A.M.E - Facial Recognition Attendance Monitoring Engine")
        self.root.geometry('1280x720')
        self.root.maxsize(CANVAS_WIDTH, CANVAS_HEIGHT)
        self.root.minsize(1280, 720)

        self.root.bind('<Escape>', self.adminMode)

        # Creates canvas, which is a child of root and sets the size of the window
        canvas = tk.Canvas(self.root, height=CANVAS_HEIGHT, width=CANVAS_WIDTH, bg='#05345C')
        canvas.pack()

        # Create a Menu Bar
        self.menubar = tk.Menu(self.root)

        # Pull-down Menu Bar Items
        self.helpmenu = tk.Menu(self.menubar, tearoff=0)
        self.helpmenu.add_command(label="Select Room", command=self.selectRoom)
        self.helpmenu.add_command(label="Student Mode", command=self.studentMode)
        self.helpmenu.add_separator()
        self.helpmenu.add_command(label="About", command=self.howToUseLabel)
        self.helpmenu.add_command(label="Credits", command=self.creditsLabel)
        self.helpmenu.add_command(label="Quit", command=self.closeQuestion)
        self.menubar.add_cascade(label="Help", menu=self.helpmenu)
        # display the menu
        self.root.config(menu=self.menubar)

        # Creates a frame for the button at the lower half of the Canvas window
        self.buttonFrame = tk.Frame(self.root, bg='#b3e6ff')
        self.buttonFrame.place(relx=0.5, rely=0.8, relwidth=0.5, relheight=0.1, anchor='n')

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
        self.stopEvent = threading.Event()

        self.thread = threading.Thread(target=self.videoLoop, args=())
        self.thread.start()
        self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)

    # Class that deals with the GUI
    def appendRoomNumber(self, value):
        self.submittedValue = self.submittedValue + str(value)
        print(self.submittedValue)
        self.roomText.config(text=self.submittedValue)

    def resetSubmittedValue(self):
        self.submittedValue = ''

    def getRoomNumber(self):
        global finalRoomNumber
        print("SUBMITTED VALUE {}".format(self.submittedValue))
        submittedValue_ = "Room_" + self.submittedValue

        if submittedValue_ in possibleRooms:
            print("Valid room given")
            finalRoomNumber = submittedValue_
            print(finalRoomNumber)
            self.resetSubmittedValue()
            self.removeSelectRoom()
        else:
            messagebox.showerror("Error", "Room Not Found")
            self.resetSubmittedValue()
            self.roomText.config(text='')

    def selectRoom(self):
        text = """Room\n\n\n\n\n"""
        self.selectRoomLab = tk.Label(FrameGUI.root, text=text, font=("Helvetica", 22), bg='#05345C',
                                      foreground="white",
                                      borderwidth=1, relief="solid")
        self.selectRoomLab.place(relx=0.77, rely=0.15, relwidth=0.21, relheight=0.31)

        self.roomText = tk.Label(FrameGUI.root, text=self.submittedValue, font=("Helvetica", 55), bg='#05345C',
                                 foreground="white")
        self.roomText.place(relx=0.77, rely=0.25, relwidth=0.21, relheight=0.1)

        self.textMessageBox = tk.Frame(self.root, bg='#05345C', borderwidth=1, relief="solid")
        self.textMessageBox.place(relx=0.5, rely=0.8, relwidth=0.5, relheight=0.15, anchor='n')

        # Buttons
        self.one_button = tk.Button(self.textMessageBox, text="0", font=("Helvetica", 22),
                                    command=lambda *args: self.appendRoomNumber(0))
        self.one_button.place(relx=0, rely=0.05, relwidth=0.1, relheight=0.5)
        self.two_button = tk.Button(self.textMessageBox, text="1", font=("Helvetica", 22),
                                    command=lambda *args: self.appendRoomNumber(1))
        self.two_button.place(relx=0.1, rely=0.05, relwidth=0.1, relheight=0.5)
        self.two_button.place(relx=0.1, rely=0.05, relwidth=0.1, relheight=0.5)
        self.three_button = tk.Button(self.textMessageBox, text="2", font=("Helvetica", 22),
                                      command=lambda *args: self.appendRoomNumber(2))
        self.three_button.place(relx=0.2, rely=0.05, relwidth=0.1, relheight=0.5)
        self.four_button = tk.Button(self.textMessageBox, text="3", font=("Helvetica", 22),
                                     command=lambda *args: self.appendRoomNumber(3))
        self.four_button.place(relx=0.3, rely=0.05, relwidth=0.1, relheight=0.5)
        self.five_button = tk.Button(self.textMessageBox, text="4", font=("Helvetica", 22),
                                     command=lambda *args: self.appendRoomNumber(4))
        self.five_button.place(relx=0.4, rely=0.05, relwidth=0.1, relheight=0.5)
        self.six_button = tk.Button(self.textMessageBox, text="5", font=("Helvetica", 22),
                                    command=lambda *args: self.appendRoomNumber(5))
        self.six_button.place(relx=0.5, rely=0.05, relwidth=0.1, relheight=0.5)
        self.seven_button = tk.Button(self.textMessageBox, text="6", font=("Helvetica", 22),
                                      command=lambda *args: self.appendRoomNumber(6))
        self.seven_button.place(relx=0.6, rely=0.05, relwidth=0.1, relheight=0.5)
        self.eight_button = tk.Button(self.textMessageBox, text="7", font=("Helvetica", 22),
                                      command=lambda *args: self.appendRoomNumber(7))
        self.eight_button.place(relx=0.7, rely=0.05, relwidth=0.1, relheight=0.5)
        self.nine_button = tk.Button(self.textMessageBox, text="8", font=("Helvetica", 22),
                                     command=lambda *args: self.appendRoomNumber(8))
        self.nine_button.place(relx=0.8, rely=0.05, relwidth=0.1, relheight=0.5)
        self.ten_button = tk.Button(self.textMessageBox, text="9", font=("Helvetica", 22),
                                    command=lambda *args: self.appendRoomNumber(9))
        self.ten_button.place(relx=0.9, rely=0.05, relwidth=0.1, relheight=0.5)

        self.submitButton = tk.Button(self.textMessageBox, text="Submit", font=("Helvetica", 22),
                                      command=self.getRoomNumber)
        self.submitButton.place(relx=0.2, rely=0.6, relwidth=0.2, relheight=0.35)
        self.cancelButton = tk.Button(self.textMessageBox, text="Cancel", font=("Helvetica", 22),
                                      command=self.removeSelectRoom)
        self.cancelButton.place(relx=0.6, rely=0.6, relwidth=0.2, relheight=0.35)
        print("[GUI] SELECT_ROOM PRINTED TO WINDOW")

    def removeSelectRoom(self):
        print("[GUI] REMOVED SELECT ROOM")
        self.selectRoomLab.destroy()
        self.resetSubmittedValue()
        self.roomText.config(text='')
        self.roomText.destroy()
        self.textMessageBox.destroy()
        self.submitButton.destroy()
        self.cancelButton.destroy()
        self.one_button.destroy()
        self.two_button.destroy()
        self.three_button.destroy()
        self.four_button.destroy()
        self.five_button.destroy()
        self.six_button.destroy()
        self.seven_button.destroy()
        self.eight_button.destroy()
        self.nine_button.destroy()
        self.ten_button.destroy()

    def howToUseLabel(self):
        print("[GUI] HOW-TO-USE PRINTED TO WINDOW")

        text = "About" + "\n\n" + "Select Room:" + "\n" + "Placeholder" + "\n\n" + "Sign in states:" + "\n" + \
               "Placeholder" + "\n\n" + "Email:" + "\n" + "Placeholder" + "\n\n" + "Student Mode:" + \
               "\n" + "Placeholder"
        self.howToUseLab = tk.Label(FrameGUI.root, text=text, font=("Helvetica", 12), bg='#05345C', foreground="white",
                                    borderwidth=1, relief="solid")
        self.howToUseLab.place(relx=0.77, rely=0.15, relwidth=0.21, relheight=0.6)
        self.howToUseButton = tk.Button(self.howToUseLab, text="Close", font=("Helvetica", 16),
                                        command=self.removeHowToUse)
        self.howToUseButton.place(relx=0.30, rely=0.85, relwidth=0.4, relheight=0.1)

    def removeHowToUse(self):
        print("[GUI] REMOVED ABOUT ROOM")
        self.howToUseLab.destroy()
        self.howToUseButton.destroy()

    def creditsLabel(self):
        print("[GUI] CREDITS PRINTED TO WINDOW")
        text = "Credits" + "\n\n" + "Programming:" + "\n" + "James Clark" + "\n\n" + "Database Design:" + "\n" + \
               "James Clark, Sam Tredgett" + "\n\n" + "Documentation:" + "\n" + "Hugo A'Violet"
        creditsLab = tk.Label(FrameGUI.root, text=text, font=("Helvetica", 11), bg='#05345C', foreground="white",
                              borderwidth=1, relief="solid")
        creditsLab.place(relx=0.77, rely=0.15, relwidth=0.2, relheight=0.3)
        creditsLab.after(4000, lambda: creditsLab.place_forget())

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
                    self.panel = tk.Label(image=image, borderwidth=1, relief="solid")
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
        p = os.path.sep.join((outputPath, filename))
        # Save file
        cv2.imwrite(p, self.frame.copy())
        print("[INFO] PHOTO SAVED TO OUTPUT DIR at", timestamp)
        # Calls facial recognition function
        computeImage(filename)

    def studentMode(self):
        self.emptyMenu = tk.Menu(self.root)
        self.root.config(menu=self.emptyMenu)
        self.root.overrideredirect(True)
        # self.menubar.entryconfig("Help", state="disabled")
        print("[GUI] STUDENT MODE ENABLED")

    def adminMode(self, event):
        self.root.config(menu=self.menubar)
        self.root.overrideredirect(False)
        print("[GUI] ADMIN MODE ENABLED")

    def closeQuestion(self):
        msgBox = tk.messagebox.askquestion('F.R.A.M.E', 'Are you sure you want to exit the application?\n'
                                                        '(This will terminate all class schedule checks)',
                                                        icon='warning')
        if msgBox == 'yes':
            FrameGUI.onClose(self)
        else:
            pass

    # Closes application when X is clicked
    def onClose(self):
        print("[INFO] APPLICATION CLOSING")
        self.stopEvent.set()
        self.vs.stop()
        self.root.quit()
        os.kill(os.getpid(), signal.SIGINT)
