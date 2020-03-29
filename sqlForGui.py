__author__ = "James Clark, Hugo A'Violet, Sam Tredgett"
__copyright__ = "Copyright 2020, F.R.A.M.E Project"
__credits__ = ["James Clark", "Hugo A'Violet", "Sam Tredgett"]
__version__ = "1.0"

# Import in necessary libraries
import time
import mysql.connector
from mysql.connector import Error
import gui
import systemtimer
import export

# Initializes user, first name and last name variables.
user = ''
fname = ''
lname = ''

# Initializes the db_name and db_name 2
db_name = ''
db_name_2 = ''

# Initializes the module code
module_code = ''
# Export list titles for the pdf
export_list = [['User ID', 'First Name', 'Last Name', 'Attended', 'Late', 'Timestamp']]

# Initializes the class variables
classDescription = ''
classDate = ''
classLength = ''
classLecturer = ''
lecturerEmail = ''


# Function that takes all of the data from the current Room Class
def exportAttendanceList():
    global db_name_2
    # Replaces the db_name_2 to not include colons, this is so it can export to the output folder
    replace = db_name_2.replace(':', '-')
    # Stores the new variable in export_file_name
    export_file_name = str(replace)
    export_module_name = str(module_code)

    try:
        connection_populate = mysql.connector.connect(host='frame-db.cvn8zxkiw7bd.us-east-1.rds.amazonaws.com',
                                                      user='admin',
                                                      password='frame2020',
                                                      )

        sql_insert_Query = """SELECT * FROM `%s`.`%s` ORDER BY classID ASC"""

        cursor = connection_populate.cursor()
        cursor.execute(sql_insert_Query, (module_code, db_name_2,))
        records = cursor.fetchall()
        print("[SQL] EXPORTED {} ATTENDANCE LIST WITH STUDENTS".format(db_name_2))

        for row in records:
            classid = (row[0])
            first_name = (row[1])
            last_name = (row[2])
            attended = (row[3])
            late = (row[4])
            time_stamp = (row[5])
            # Stores all of data from each row in a values list
            values = [classid, first_name, last_name, attended, late, time_stamp]
            # Adds each values list to the export list of lists
            export_list.append(values)

        print(export_list)
        # Calls the export to PDF function
        # @params - export list, the module code and the filename
        export.exportToPDF(export_list, export_module_name, export_file_name)

    except Error as e:
        print("Error reading data from MySQL table", e)

    finally:
        if connection_populate.is_connected():
            connection_populate.close()
            cursor.close()


# Function that deletes all of the data from the Room class table
def clearTempClassTable():
    global db_name

    try:
        connection_clear = mysql.connector.connect(host='frame-db.cvn8zxkiw7bd.us-east-1.rds.amazonaws.com',
                                                   database='frame_database',
                                                   user='admin',
                                                   password='frame2020',
                                                   )

        sql_insert_Query = """DELETE FROM `%s`"""

        cursor = connection_clear.cursor()
        cursor.execute(sql_insert_Query, (db_name,))
        connection_clear.commit()
        print("[SQL] CLEARED TEMP ROOM".format(db_name))

    except Error as e:
        print("Error reading data from MySQL table", e)
    finally:
        if connection_clear.is_connected():
            connection_clear.close()
            cursor.close()


# Populate function that takes the data from the module_code table
# Inserts the data into the Room table
def populateAttendanceList(module_code):
    global db_name
    db_name = gui.finalRoomNumber + "_Temp"

    try:
        connection_populate = mysql.connector.connect(host='frame-db.cvn8zxkiw7bd.us-east-1.rds.amazonaws.com',
                                                      database='frame_database',
                                                      user='admin',
                                                      password='frame2020',
                                                      )

        sql_insert_Query = """INSERT INTO `%s` (classID, first_name, last_name, attended, late, time_stamp)
                              SELECT userID, first_name, last_name, (%s), (%s), (%s) FROM `%s`
                              ORDER BY userID ASC"""

        cursor = connection_populate.cursor()
        cursor.execute(sql_insert_Query, (db_name, None, None, None, module_code))
        connection_populate.commit()
        print("[SQL] POPULATED {} ATTENDANCE LIST WITH STUDENTS".format(db_name))

    except Error as e:
        print("Error reading data from MySQL table", e)
    finally:
        if connection_populate.is_connected():
            connection_populate.close()
            cursor.close()


# Creates a new attendanceList table
# Stores the data in the current module_code database
# Creates the table name: module_code + class_start_date
def createAttendanceList(module_code, current_time_and_date):
    global db_name
    global db_name_2
    db_name_2 = str(module_code + " : " + current_time_and_date)

    try:
        connection_create = mysql.connector.connect(host='frame-db.cvn8zxkiw7bd.us-east-1.rds.amazonaws.com',
                                                    user='admin',
                                                    password='frame2020',
                                                    )

        sql_create_Query = """CREATE TABLE `%s`.`%s` LIKE frame_database.`%s`"""

        cursor = connection_create.cursor()
        cursor.execute(sql_create_Query, (module_code, db_name_2, db_name))
        print("[SQL] CREATED {} ATTENDANCE LIST".format(db_name_2))
        populateNewAttendanceList()
        clearTempClassTable()

    except Error as e:
        print("Error reading data from MySQL table", e)
    finally:
        if connection_create.is_connected():
            connection_create.close()
            cursor.close()


# Populates the newly created table with the data from the Room Class Table
def populateNewAttendanceList():
    global db_name_2
    global db_name

    try:
        connection_populate = mysql.connector.connect(host='frame-db.cvn8zxkiw7bd.us-east-1.rds.amazonaws.com',
                                                      user='admin',
                                                      password='frame2020',
                                                      )

        sql_populate_Query = """INSERT INTO `%s`.`%s` SELECT * FROM frame_database.`%s`"""

        cursor = connection_populate.cursor()
        cursor.execute(sql_populate_Query, (module_code, db_name_2, db_name))
        connection_populate.commit()
        print("[SQL] COPIED DATA {} ATTENDANCE LIST".format(db_name_2))

        # Once this has been populated it calls the exportAttendanceList function
        time.sleep(1)
        exportAttendanceList()

    except Error as e:
        print("Error reading data from MySQL table", e)
    finally:
        if connection_populate.is_connected():
            connection_populate.close()
            cursor.close()


# Function that continually checks the date/time matches a classDate from the current room
def getClassDate(current_time_and_date, room_number):
    global TimeAndDate
    timeAndDate = current_time_and_date
    time = 0
    try:
        connection = mysql.connector.connect(host='frame-db.cvn8zxkiw7bd.us-east-1.rds.amazonaws.com',
                                             database='frame_database',
                                             user='admin',
                                             password='frame2020',
                                             )

        sql_update_Query = """ SELECT * FROM `%s` WHERE classDate = (%s) """
        cursor = connection.cursor()
        cursor.execute(sql_update_Query, (room_number, current_time_and_date,))
        records = cursor.fetchall()

        global module_code
        global classDescription
        global classDate
        global classLength
        global classLecturer
        global lecturerEmail

        for row in records:
            print(row[1])
            module_code = row[1]
            print(row[2])
            classDescription = row[2]
            print(row[3])
            classDate = str(row[3])
            time = row[4]
            classLength = row[4]
            print(row[5])
            classLecturer = row[5]
            print(row[6])
            lecturerEmail = row[6]

        if time > 0:
            gui.updateGUIClassDetails()
            populateAttendanceList(module_code)
            systemtimer.startSystemTimer(time)

    except Error as e:
        print("Error reading data from MySQL table", e)
    finally:
        if connection.is_connected():
            connection.close()
            cursor.close()


# Updates the SQL Database with the User's timestamp
# @param userID - Student's ID
# @param timestamp - filename with removed extension
def updateTimeStamp(userID, timestamp):
    database_name = db_name
    try:
        connection = mysql.connector.connect(host='frame-db.cvn8zxkiw7bd.us-east-1.rds.amazonaws.com',
                                             database='frame_database',
                                             user='admin',
                                             password='frame2020',
                                             )

        sql_update_Query = """ UPDATE `%s` SET time_stamp = (%s)
                               WHERE classID = (%s)"""
        cursor = connection.cursor()
        cursor.execute(sql_update_Query, (database_name, timestamp, userID,))
        connection.commit()

    except Error as e:
        print("Error reading data from MySQL table", e)
    finally:
        if connection.is_connected():
            connection.close()
            cursor.close()


# Updates the Class Table 'Late' field if User is late
# @param userID - Student's ID
def updateClassTableLate(userID):
    database_name = db_name
    try:
        connection = mysql.connector.connect(host='frame-db.cvn8zxkiw7bd.us-east-1.rds.amazonaws.com',
                                             database='frame_database',
                                             user='admin',
                                             password='frame2020',
                                             )

        sql_update_Query = """ UPDATE `%s` SET late = 'YES'
                               WHERE classID = (%s)"""
        cursor = connection.cursor()
        cursor.execute(sql_update_Query, (database_name, userID,))
        connection.commit()



    except Error as e:
        print("Error reading data from MySQL table", e)
    finally:
        if connection.is_connected():
            connection.close()
            cursor.close()


# Updates the Class Table 'Attended' field
# @param userID - Student's ID
def updateClassTable(userID):
    database_name = db_name
    try:
        connection = mysql.connector.connect(host='frame-db.cvn8zxkiw7bd.us-east-1.rds.amazonaws.com',
                                             database='frame_database',
                                             user='admin',
                                             password='frame2020',
                                             )

        sql_update_Query = """ UPDATE `%s` SET attended = 'YES'
                               WHERE classID = (%s)"""
        cursor = connection.cursor()
        cursor.execute(sql_update_Query, (database_name, userID,))
        connection.commit()


    except Error as e:
        print("Error reading data from MySQL table", e)
    finally:
        if connection.is_connected():
            connection.close()
            cursor.close()


# Prints out variables
def printUserInfo():
    print(user)
    print(fname)
    print(lname)


# Reads the User's information and stores their User Information in three variables
# @param userID - Student's ID
# user = userID
# fname = First Name
# lname = Last Name
def readUserData(userID):
    try:
        connection = mysql.connector.connect(host='frame-db.cvn8zxkiw7bd.us-east-1.rds.amazonaws.com',
                                             database='frame_database',
                                             user='admin',
                                             password='frame2020',
                                             use_pure=True)
        sql_select_Query = """SELECT * FROM Students WHERE userID = (%s)"""
        cursor = connection.cursor()
        cursor.execute(sql_select_Query, (userID,))
        records = cursor.fetchall()

        global user
        global fname
        global lname

        for row in records:
            user = row[0]
            fname = row[1]
            lname = row[2]



    except Error as e:
        print("Error reading data from MySQL table", e)
    finally:
        if connection.is_connected():
            connection.close()
            cursor.close()
