__author__ = "James Clark"
__copyright__ = "Copyright 2020, F.R.A.M.E Project"
__credits__ = ["James Clark"]
__version__ = "1.0"

# Import in necessary libraries
import time

import mysql.connector
from mysql.connector import Error
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

import smtplib
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Attendance value starts at 0
attendance_value = 0
# Counter to increment the attendance value
counter = 1
# List of studentID's and their attendance value
attend = []
# List of all tables in the specific module database
tables = []

# Initializes module_code
module_code = ''


# Populates the default attend list with student id's who are taking that module.
# Populates it with their studentid and an attendance value of 0.
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

    except Error as e:
        print("Error reading data from MySQL table", e)

    finally:
        if connection.is_connected():
            connection.close()
            cursor.close()


# Gets all the class table names that are associated with that module_code database.
# Appends the module code titles and adds them to the tables list.
def getClassTableNames(mod_code):
    global attend

    try:
        connection_two = mysql.connector.connect(host='frame-db.cvn8zxkiw7bd.us-east-1.rds.amazonaws.com',
                                                 user='admin',
                                                 password='frame2020',
                                                 )

        sql_get_Query = """SHOW TABLES IN `%s`"""

        cursor = connection_two.cursor()
        cursor.execute(sql_get_Query, (mod_code,))
        for (table_name,) in cursor:
            result = table_name.replace("'", "")
            tables.append(result)

    except Error as e:
        print("Error reading data from MySQL table", e)

    finally:
        if connection_two.is_connected():
            connection_two.close()
            cursor.close()


# Checks each row in the class table.
# If 'Attended' in a row matches 'YES' then:
# prints the USER ID
# Enumerates over the  attended lists, checks if classID matches a student id.
# Once a match is found it adds counter to the attendance value.
# If not attended, do nothing.
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


# Matpotlib creating the table.
# Splits the users and attendance into two lists.
# Exports it to a pdf and saves it in the path location specified in main.

def createBarChart():
    users, attendance = [*zip(*attend)]
    print(users)
    print(attendance)

    ypos = np.arange(len(users))

    with PdfPages(path) as export_pdf:
        plt.xticks(ypos, users)
        plt.xlabel("Student ID's")
        plt.ylabel("Amount of Classes")
        plt.title("{} Attendance".format(module_code))
        plt.bar(ypos, attendance)
        export_pdf.savefig()
        plt.close()


# Sends the email to the lecturer
# @params pdf = the pdf that was generated
def emailPDF(pdf, name):
    # Sets the filename to the pdf
    filename = pdf
    title = filename
    subject = name
    body = "\n" \
           + "Attendance data attached: {}".format(subject) \
           + "\n" \
           + "This is an automated email sent by F.R.A.M.E."

    sender_email = "frame.project600@gmail.com"
    receiver_email = email_address

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Bcc"] = receiver_email  # Recommended for mass emails

    # Add body to email
    message.attach(MIMEText(body, "plain"))

    # Open PDF file in binary mode
    with open(pdf, "rb") as attachment:
        # Add file as application/octet-stream
        # Email client can usually download this automatically as attachment
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    # Encode file in ASCII characters to send by email
    encoders.encode_base64(part)

    # Add header as key/value pair to attachment part
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {title}",
    )

    # Add attachment to message and convert message to string
    message.attach(part)
    text = message.as_string()

    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, "F.R.A.M.E2020")
        server.sendmail(sender_email, receiver_email, text)


# Starts the program.
# Module code: input in the module code to check the database.
# Email address: input in the email address you want the visual data to be sent to.
if __name__ == "__main__":
    exec(open('scripts/splashscreen_data.py').read())
    print("F.R.A.M.E Attendance Analytics")
    time.sleep(0.5)
    print("Enter the module code:")
    module_code = input()
    time.sleep(0.5)
    print("Enter email address:")
    email_address = input()
    print("Generating visual data...")

    file_name = module_code + " - Attendance Data"
    path = ("PDF/" + module_code + "/data/" + file_name + ".pdf")
    populateDefaultAttendList(module_code)
    getClassTableNames(module_code)

    for i in tables:
        print("\n\n\n\nTABLE " + str(i) + ": ")
        getClassData(i, module_code)

createBarChart()
emailPDF(path, file_name)
print("Sent visual data to: {}".format(email_address))
