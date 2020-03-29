__author__ = "James Clark, Hugo A'Violet, Sam Tredgett"
__copyright__ = "Copyright 2020, F.R.A.M.E Project"
__credits__ = ["James Clark", "Hugo A'Violet", "Sam Tredgett"]
__version__ = "1.0"

# Import in necessary libraries
import time

import sqlForGui
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table

import smtplib
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Stores the logo
logo = 'images/uok_logo.jpg'
# Sets width and height variables to equal the letter
Width, Height = letter
# Stores the title heading
Title = "Attendance List"


# Defines the first page and draws the logo into the top left corner.
def myFirstPage(canvas, pdf):
    canvas.saveState()
    canvas.drawImage(logo, 0, 710, width=100, height=100, preserveAspectRatio=True)


# Exports the PDF with the current export list, module code and filename
def exportToPDF(export_list, export_module_code, export_filename):
    data = export_list
    filename = ("PDF/" + export_module_code + "/" + export_filename + ".pdf")
    pdf = SimpleDocTemplate(
        filename,
        pagesize=letter
    )

    table = Table(data)

    # Styling
    from reportlab.platypus import TableStyle
    from reportlab.lib import colors

    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#05345C')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ])

    table.setStyle(style)

    # Add borders
    ts = TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('LINEABOVE', (0, 1), (-1, -1), 1, colors.black),
        ('GRID', (0, 1), (-1, 0), 1, colors.black),
    ])

    table.setStyle(ts)

    elems = [table]
    pdf.build(elems, onFirstPage=myFirstPage)
    time.sleep(1)
    # Calls the sendEmailToLecturer function
    sendEmailToLecturer(filename)


# Sends the email to the lecturer
# @params pdf = the pdf that was generated
def sendEmailToLecturer(pdf):
    subject = str(sqlForGui.db_name_2)
    body = "Automated email, send with attached attendance form - F.R.A.M.E"
    sender_email = "frame.project600@gmail.com"
    receiver_email = str(sqlForGui.lecturerEmail)

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Bcc"] = receiver_email  # Recommended for mass emails

    # Add body to email
    message.attach(MIMEText(body, "plain"))

    # Sets the filename to the pdf
    # Sets the title of the document to the filename directory removing the folder names
    filename = pdf
    title = filename[10:]

    # Open PDF file in binary mode
    with open(filename, "rb") as attachment:
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
