# F.R.A.M.E - Facial Recognition Attendance Monitoring Engine
## Project Description
F.R.A.M.E is a fully functional attendance monitoring system designed to be used within educational institutions to mark students as attended. The system uses facial recognition to mark the student as attendance or late. The system uses a GUI and has been designed to be used on touch-screen monitors. To know more about the system please watch the project video demo:

[![Video thumbnail](https://img.youtube.com/vi/RBPeUJZwJ54/0.jpg)](https://youtu.be/RBPeUJZwJ54)

## How to use

* Enter database information into sqlForGui.py (change fields if nesseccary, defaults are: UserID, firstName, lastName, photo)
* Run guiTest.py, enter in the relevant userID, if a photo is stored within mySQL as BLOB it will pull that photo.
* Stores the photo into dir/images/{userID}.jpg
* Retrieves photo and displays it within the GUI
* Can also pull relevant fields and display within the CL, by submitting the UserID.

## Built With

* [Python 3 ](https://docs.python.org/3/) - Programming language
* [Tkinter ](https://docs.python.org/3/library/tkinter.html) - GUI Library
* [AWS ](https://aws.amazon.com/) - AWS using mySQL 


* [Python](https://www.python.org/) - Programming language
* [openCV](https://opencv.org/) - Python Libary
* [mySQL](https://www.mysql.com/) - Database
* [AWS](https://aws.amazon.com/) - Cloud Storage
* [Trello](http://trello.com/) - Team communication
