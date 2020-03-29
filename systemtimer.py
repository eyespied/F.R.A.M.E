__author__ = "James Clark, Hugo A'Violet, Sam Tredgett"
__copyright__ = "Copyright 2020, F.R.A.M.E Project"
__credits__ = ["James Clark", "Hugo A'Violet", "Sam Tredgett"]
__version__ = "1.0"

# Import in necessary libraries
import threading
import time
import sqlForGui
import gui
from datetime import datetime, date

current_time_and_date = ''


# Function that runs the system timer
# When the system timer is 0, updates the SQL database with late and attended SQL queries

def systemTimer(system_timer):
    global timerOver
    global classCheckOver
    # Variable that defines the time the system variable takes to finish
    while system_timer > 15:
        timerOver = False
        classCheckOver = False
        time.sleep(1)
        system_timer -= 1
        print("CLASS OVER IN {}".format(system_timer))

    timerOver = True
    print("[SQL] UPDATING CLASS DATABASE")

    # Calls two functions to update SQL database
    for i in gui.attendees:
        sqlForGui.updateClassTable(i)

    for i in gui.late_attendees:
        sqlForGui.updateClassTableLate(i)

    # frame.ifClass = False
    export_module_name = str(sqlForGui.module_code)
    sqlForGui.createAttendanceList(export_module_name, current_time_and_date)


def getCurrentTimeAndDate():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    today = date.today()

    global current_time_and_date
    current_time_and_date = str(today) + " " + current_time
    print(current_time_and_date)
    sqlForGui.getClassDate(current_time_and_date, gui.finalRoomNumber)


classCheckOver = True


def classCheck():
    timer = 0
    global classCheckOver

    # Variable that defines the time the system variable takes to finish
    while timer > 0:
        time.sleep(1)
        timer -= 1

    classCheckOver = True
    if classCheckOver:
        print("[SQL] CHECKING IF CLASS FOUND")
        getCurrentTimeAndDate()
        classCheck()


def startSystemTimer(class_length):
    # Starts thread for class timer

    system_thread = threading.Thread(target=systemTimer, args=(class_length,))
    late_thread = threading.Thread(target=lateTimer, args=(class_length / 2,))

    system_thread.start()
    late_thread.start()

    system_thread.join()
    late_thread.join()


isLate = False


# lateTimer that activates when late_timer reaches
def lateTimer(late_timer):
    global isLate
    # Late timer variable (seconds) change this to change the timer.
    while late_timer > 0:
        time.sleep(1)
        late_timer -= 1
        print("LATER TIMER IN: {}".format(str(late_timer)))

    isLate = True
    if isLate:
        print("[INFO] USERS WILL NOW BE MARKED AS LATE")
