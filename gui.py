import tkinter as tk
import threading
import cv2
import face_recognition
from PIL import Image, ImageTk
import datetime
import os


# class resizeImages:
#
#     # Resize's the Take Photo Button to be relative to fit window screen
#     def resize_image(event):
#         new_width = event.width
#         new_height = event.height
#         image = FrameGUI.buttonImageCopy.resize((new_width, new_height))
#         photo = ImageTk.PhotoImage(image)
#         FrameGUI.button.config(image=photo)
#         FrameGUI.button.image = photo  # avoid garbage collection
#
#     def resize_image2(event):
#         new_width = event.width
#         new_height = event.height
#         image = FrameGUI.titleImageCopy.resize((new_width, new_height))
#         photo = ImageTk.PhotoImage(image)
#         FrameGUI.title.config(image=photo)
#         FrameGUI.title.image = photo  # avoid garbage collection
#
#     def resize_image3(event):
#         new_width = event.width
#         new_height = event.height
#         image = FrameGUI.background_imageCopy.resize((new_width, new_height))
#         photo = ImageTk.PhotoImage(image)
#         FrameGUI.background_label.config(image=photo)
#         FrameGUI.background_label.image = photo  # avoid garbage collection
#
#     def resize_image4(event):
#         new_width = event.width
#         new_height = event.height
#         image = FrameGUI.howToUseButton_Copy.resize((new_width, new_height))
#         photo = ImageTk.PhotoImage(image)
#         FrameGUI.button2.config(image=photo)
#         FrameGUI.button2.image = photo  # avoid garbage collection

class BreakIt(Exception): pass


def computeImage(filename):
    print("[INFO] CROSS-REFERENCING IMAGE")
    print(filename)
    # Recognizing Face from photo Saved
    var = 0

    directory = "output/"
    file_names = os.listdir(directory)

    picture_of_me = face_recognition.load_image_file("rawimages/{}".format(filename))
    my_face_encoding = face_recognition.face_encodings(picture_of_me)[0]

    print("[INFO] CHECKING IF USER IS IN DATABASE")
    try:
        for i in file_names:
            iPath = os.path.join(directory, i)
            with open(iPath, 'rb') as fh:

                new_picture = face_recognition.load_image_file(iPath)

                for face_encoding in face_recognition.face_encodings(new_picture):

                    results = face_recognition.compare_faces([my_face_encoding], face_encoding)

                    if results[0]:
                        print("[INFO] USER FOUND")
                        userID = ''.join(filter(lambda x: x.isdigit(), iPath))
                        print("[INFO] ID : {}".format(userID))
                        raise BreakIt
                    else:
                        pass
    except BreakIt:
        pass


class FrameGUI:
    def __init__(self, vs):
        self.outputPath = 'rawimages'
        self.vs = vs
        self.frame = None
        self.thread = None
        self.stopEvent = None
        # Initialize root window
        self.root = tk.Tk()
        self.panel = None

        # Parameters to store int values for size of window
        CANVAS_HEIGHT = 720
        CANVAS_WIDTH = 1280

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

    def takeImage(self):
        timestamp = datetime.datetime.now()
        filename = "{}.jpg".format(timestamp.strftime("%Y-%m-%d_%H-%M-%S"))
        p = os.path.sep.join((self.outputPath, filename))
        # Save file
        cv2.imwrite(p, self.frame.copy())
        print("[INFO] PHOTO SAVED TO OUTPUT DIR at", timestamp)
        computeImage(filename)

    def onClose(self):
        print("[INFO] APPLICATION CLOSING")
        self.stopEvent.set()
        self.vs.stop()
        self.root.quit()
