from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from email.message import EmailMessage
import ssl
from rest_framework.response import Response
from rest_framework import status
from payroll_project.settings import EMAIL_HOST, EMAIL_HOST_USER , EMAIL_HOST_PASSWORD, EMAIL_PORT

def send_leave_email(user_email, subject, message):
    sender_email = EMAIL_HOST_USER
    password = EMAIL_HOST_PASSWORD
    if not password:
        raise ValueError("Password is Incorrect")
    
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = user_email
    msg.set_content(message)
    
    with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT) as server:
        server.login(EMAIL_HOST_USER , EMAIL_HOST_PASSWORD)
        server.send_message(msg)