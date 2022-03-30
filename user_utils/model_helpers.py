"""
model helpers
"""
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.core.exceptions import ValidationError

##### Functions #####
def _send_email(from_email, from_password, reciepient_emails, smtp_server, smtp_port, subject, text_content, html_content):
    """
    Sends an email message from the sender's email to the reciever's email 

    Inputs
        :param from_email: <str> of sender's email
        :param from_password: <str> of sender's password
        :param reciepient_emails: <list> of reciever emails
        :param smtp_server: <str> of email host's smtp server
        :param smtp_port: <str>  port to connect to (usually 993)
        :param subject: <str> describing the message to be sent
        :param text_content: <str> detailing the message's text content to send 
        :param html_content: <str> detailing the message's html content to send 
    """
    try:
        server = smtplib.SMTP("localhost")
        if from_password is not None:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port, context = ssl.create_default_context())
            server.login(from_email, from_password)
            print("Successfully logged in ...")

        for receiver_email in reciepient_emails:
            print("Sending to %s" % receiver_email)
            message            = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"]    = from_email
            message["To"]      = receiver_email
            part_1             = MIMEText(text_content, "plain")
            part_2             = MIMEText(html_content, "html")

            message.attach(part_1)
            server.sendmail(from_email, receiver_email, message.as_string())

    except Exception as error:
        print("Error: %s" % error)
        
    finally:
        server.quit() 