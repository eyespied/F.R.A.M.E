__author__ = "James Clark, Hugo A'Violet, Sam Tredgett"
__copyright__ = "Copyright 2020, F.R.A.M.E Project"
__credits__ = ["James Clark", "Hugo A'Violet", "Sam Tredgett"]
__version__ = "1.0"

import mysql.connector
from mysql.connector import Error

import gui
import systemtimer
import export

# Initializes user, first name and last name variables.
user = ''
fname = ''
lname = ''

db_name = ''
module_code = ''
export_list = [['User ID', 'First Name', 'Last Name', 'Attended', 'Late', 'Timestamp']]

classDescription = ''
classDate = ''
classLength = ''
classLecturer = ''
lecturerEmail = ''

# TODO:
#       - Save class data from the class and copy it to a new table in a new database.
#       - Clear class data from the class table
#       - Update class data when new class is found
#       - Repeat process


def exportAttendanceList(module_code_, database_name):
    global db_name
    db_name = database_name
    replace = db_name.replace(':', '-')
    export_file_name = str(replace)
    export_module_name = str(module_code_)

    try:
        connection_populate = mysql.connector.connect(host='frame-db.cvn8zxkiw7bd.us-east-1.rds.amazonaws.com',
                                                      database='frame_database',
                                                      user='admin',
                                                      password='frame2020',
                                                      )

        sql_insert_Query = """SELECT * FROM `%s` ORDER BY classID ASC"""

        cursor = connection_populate.cursor()
        cursor.execute(sql_insert_Query, (db_name,))
        records = cursor.fetchall()
        print("[SQL] EXPORTED {} ATTENDANCE LIST WITH STUDENTS".format(db_name))

        for row in records:
            classid = (row[0])
            first_name = (row[1])
            last_name = (row[2])
            attended = (row[3])
            late = (row[4])
            time_stamp = (row[5])
            values = [classid, first_name, last_name, attended, late, time_stamp]
            export_list.append(values)

        print(export_list)
        export.exportToPDF(export_list, export_module_name, export_file_name)


    except Error as e:
        print("Error reading data from MySQL table", e)
    finally:
        if connection_populate.is_connected():
            connection_populate.close()
            cursor.close()


def populateAttendanceList(module_code, current_time_and_date):
    global db_name
    db_name = str(module_code + " : " + current_time_and_date)

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


def createAttendanceList(module_code, current_time_and_date):
    global db_name
    db_name = str(module_code + " : " + current_time_and_date)
    try:
        connection_create = mysql.connector.connect(host='frame-db.cvn8zxkiw7bd.us-east-1.rds.amazonaws.com',
                                                    database='frame_database',
                                                    user='admin',
                                                    password='frame2020',
                                                    )

        sql_create_Query = """CREATE TABLE `%s` LIKE `class_template`"""

        cursor = connection_create.cursor()
        cursor.execute(sql_create_Query, (db_name,))
        print("[SQL] CREATED {} ATTENDANCE LIST".format(db_name))

        populateAttendanceList(module_code, current_time_and_date)

    except Error as e:
        print("Error reading data from MySQL table", e)
    finally:
        if connection_create.is_connected():
            connection_create.close()
            cursor.close()


def getClassDate(current_time_and_date, room_number):
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
            createAttendanceList(module_code, current_time_and_date)
            gui.updateGUIClassDetails()
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
