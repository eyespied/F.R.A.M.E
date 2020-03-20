__author__ = "James Clark, Hugo A'Violet, Sam Tredgett"
__copyright__ = "Copyright 2020, F.R.A.M.E Project"
__credits__ = ["James Clark", "Hugo A'Violet", "Sam Tredgett"]
__version__ = "1.0"

# Import in necessary libraries
import time
import sqlForGui
import gui


# Function that runs the system timer
# When the system timer is 0, updates the SQL database with late and attended SQL queries

def systemTimer():
    global timerOver
    global system_timer

    # Variable that defines the time the system variable takes to finish
    system_timer = 20
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
