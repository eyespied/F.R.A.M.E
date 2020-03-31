import time

import mysql.connector
from mysql.connector import Error
import matplotlib.pyplot as plt
import numpy as np

# Attend list for co_600
# One list contains, student id, attend value (default = 0)

attendance_value = 0
counter = 1
attend = []
tables = []

module_code = ''


# Function that takes all of the data from the current Room Class
def populateDefaultAttendList(mod_code):
    global attend
    try:
        connection = mysql.connector.connect(host='frame-db.cvn8zxkiw7bd.us-east-1.rds.amazonaws.com',
                                             user='admin',
                                             password='frame2020',
                                             database='frame_database'
                                             )

        sql_get_Query = """SELECT * FROM frame_database.`%s` ORDER BY userID ASC"""

        cursor = connection.cursor()
        cursor.execute(sql_get_Query, (mod_code,))
        records = cursor.fetchall()

        for row in records:
            userID = row[0]
            values = [userID, attendance_value]
            attend.append(values)

        print("EMPTY LIST: " + str(attend))

    except Error as e:
        print("Error reading data from MySQL table", e)

    finally:
        if connection.is_connected():
            connection.close()
            cursor.close()


# Function that takes all of the data from the current Room Class
def getClassData(table_name, mod_code):
    global attend
    global attendance_value
    global counter

    try:
        connection_two = mysql.connector.connect(host='frame-db.cvn8zxkiw7bd.us-east-1.rds.amazonaws.com',
                                                 user='admin',
                                                 password='frame2020',
                                                 )

        sql_get_Query = """SELECT * FROM `%s`.`%s` ORDER BY classID ASC"""

        cursor = connection_two.cursor()
        cursor.execute(sql_get_Query, (mod_code, table_name,))
        records = cursor.fetchall()

        for row in records:
            classID = row[0]
            attended = row[3]
            if attended == 'YES':
                print("USER ID: " + str(classID) + " UPDATED")

                for index, sublist in enumerate(attend):
                    if sublist[0] == classID:
                        attend[index][1] += counter
                        break

            else:
                pass

        print(attend)
    except Error as e:
        print("Error reading data from MySQL table", e)

    finally:
        if connection_two.is_connected():
            connection_two.close()
            cursor.close()


def getClassTableNames(mod_code):
    global attend

    try:
        connection_two = mysql.connector.connect(host='frame-db.cvn8zxkiw7bd.us-east-1.rds.amazonaws.com',
                                                 user='admin',
                                                 password='frame2020',
                                                 )

        sql_get_Query = """SHOW TABLES IN `%s`"""

        cursor = connection_two.cursor()
        cursor.execute(sql_get_Query,(mod_code,))
        for (table_name,) in cursor:
            result = table_name.replace("'", "")
            tables.append(result)

        print("TABLES: " + str(tables))

    except Error as e:
        print("Error reading data from MySQL table", e)

    finally:
        if connection_two.is_connected():
            connection_two.close()
            cursor.close()


def creatBarChart():
    users, attendance = [*zip(*attend)]
    print(users)
    print(attendance)

    ypos = np.arange(len(users))

    plt.xticks(ypos, users)
    plt.xlabel("Student ID's")
    plt.ylabel("Amount of Classes")
    plt.title("{} Attendance".format(module_code))
    plt.bar(ypos, attendance)
    plt.show()


if __name__ == "__main__":

    print("F.R.A.M.E Attendance Analytics")
    time.sleep(0.5)
    print("Enter the module code below:")
    module_code = input()
    print("Module code: " + module_code)
    time.sleep(0.5)
    print("Generating visual data...")
    populateDefaultAttendList(module_code)
    getClassTableNames(module_code)

    for i in tables:
        print("\n\n\n\nTABLE " + str(i) + ": ")
        getClassData(i, module_code)

creatBarChart()
