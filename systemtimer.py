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
    # Variable that defines the time the system variable takes to finish
    while system_timer > 0:
        timerOver = False
        time.sleep(1)
        system_timer -= 1

    timerOver = True
    if timerOver:
        print("[SQL] UPDATING CLASS DATABASE")

        # Calls two functions to update SQL database
        for i in gui.attendees:
            sqlForGui.updateClassTable(i)

        for i in gui.late_attendees:
            sqlForGui.updateClassTableLate(i)

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


def classCheck():
    timer = 0
    global classCheckOver

    # Variable that defines the time the system variable takes to finish
    while timer > 0:
        classCheckOver = False
        time.sleep(1)
        timer -= 1

    classCheckOver = True
    if classCheckOver:
        print("[SQL] CHECKING IF CLASS FOUND")
        getCurrentTimeAndDate()
        classCheck()


def startSystemTimer(class_length):
    # Starts thread for class timer
    late_thread = threading.Thread(target=gui.lateTimer(30))
    system_thread = threading.Thread(target=systemTimer(class_length - 11))

    late_thread.start()
    system_thread.start()

