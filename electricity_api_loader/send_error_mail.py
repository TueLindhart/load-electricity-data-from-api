import os
import smtplib
from email.message import EmailMessage


def send_email(content: str):
    """
    Sends an email using the provided subject and content.

    :param subject: Subject of the email.
    :param content: Content/body of the email.
    :param to_email: Recipient's email address.
    """

    # Email settings
    smtp_server = "smtp.gmail.com"  # The SMTP server of your email provider
    smtp_port = 587  # The SMTP port. Common ports are 587 (for TLS) and 465 (for SSL).
    from_email: str = os.getenv("FROM_EMAIL")  # type: ignore
    from_password: str = os.getenv("FROM_PASSWORD")  # type: ignore

    # Create an EmailMessage object
    msg = EmailMessage()
    msg.set_content(content)
    msg["Subject"] = "Electricity data load error"
    msg["From"] = from_email
    msg["To"] = os.getenv("TO_EMAIL")

    # Establish a connection to the SMTP server
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()  # Upgrade the connection to encrypted TLS
        server.login(from_email, from_password)  # Login to your email account
        server.send_message(msg)  # Send the email message


if __name__ == "__main__":
    send_email(content="Aprilsnar! Alt godt")
