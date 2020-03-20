__author__ = "James Clark, Hugo A'Violet, Sam Tredgett"
__copyright__ = "Copyright 2020, F.R.A.M.E Project"
__credits__ = ["James Clark", "Hugo A'Violet", "Sam Tredgett"]
__version__ = "1.0"

# Import in necessary libraries
import mysql.connector
from mysql.connector import Error

# Initializes user, first name and last name variables.
user = ''
fname = ''
lname = ''


# Prints out variables
def printUserInfo():
    print(user)
    print(fname)
    print(lname)


# Updates the SQL Database with the User's timestamp
# @param userID - Student's ID
# @param timestamp - filename with removed extension
def updateTimeStamp(userID, timestamp):
    try:
        connection = mysql.connector.connect(host='frame-db.cvn8zxkiw7bd.us-east-1.rds.amazonaws.com',
                                             database='frame_db',
                                             user='admin',
                                             password='frame2020',
                                             )

        sql_update_Query = """ UPDATE Class_Example SET timestamp = (%s)
                               WHERE userID = (%s)"""
        cursor = connection.cursor()
        cursor.execute(sql_update_Query, (timestamp, userID,))
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
    try:
        connection = mysql.connector.connect(host='frame-db.cvn8zxkiw7bd.us-east-1.rds.amazonaws.com',
                                             database='frame_db',
                                             user='admin',
                                             password='frame2020',
                                             )

        sql_update_Query = """ UPDATE Class_Example SET late = 'YES'
                               WHERE userID = (%s)"""
        cursor = connection.cursor()
        cursor.execute(sql_update_Query, (userID,))
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
    try:
        connection = mysql.connector.connect(host='frame-db.cvn8zxkiw7bd.us-east-1.rds.amazonaws.com',
                                             database='frame_db',
                                             user='admin',
                                             password='frame2020',
                                             )

        sql_update_Query = """ UPDATE Class_Example SET attended = 'YES'
                               WHERE userID = (%s)"""
        cursor = connection.cursor()
        cursor.execute(sql_update_Query, (userID,))
        connection.commit()


    except Error as e:
        print("Error reading data from MySQL table", e)
    finally:
        if connection.is_connected():
            connection.close()
            cursor.close()


# Reads the User's information and stores their User Information in three variables
# @param userID - Student's ID
# user = userID
# fname = First Name
# lname = Last Name
def readUserData(userID):
    try:
        connection = mysql.connector.connect(host='frame-db.cvn8zxkiw7bd.us-east-1.rds.amazonaws.com',
                                             database='frame_db',
                                             user='admin',
                                             password='frame2020',
                                             use_pure=True)
        sql_select_Query = """SELECT * FROM Users WHERE userID = (%s)"""
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


# Everything below this is experimental and not needed for the prototype

def write_file(data, filename):
    # Convert binary data to proper format and write it on Hard Disk
    with open(filename, 'wb') as file:
        file.write(data)


def readBLOB(userID, photo):
    print("Reading BLOB data from Users table")

    try:
        connection = mysql.connector.connect(host='',
                                             database='',
                                             user='',
                                             password='')

        cursor = connection.cursor()
        sql_fetch_blob_query = """SELECT * from Users where userID = %s"""

        cursor.execute(sql_fetch_blob_query, (userID,))
        record = cursor.fetchall()
        for row in record:
            print("Id = ", row[0], )
            print("First Name = ", row[1])
            print("Last Name = ", row[2])
            image = row[3]
            print("Storing User image and on disk \n")
            write_file(image, photo)

    except mysql.connector.Error as error:
        print("Failed to read BLOB data from MySQL table {}".format(error))

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")
