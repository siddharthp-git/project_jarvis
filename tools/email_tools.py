import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email_macos(recipient: str, subject: str = "", body: str = "") -> str:
    """
    Sends an email directly via Gmail SMTP.
    Credentials are read from config.py (GMAIL_ADDRESS and GMAIL_APP_PASS).

    Args:
        recipient: The email address to send to.
        subject:   Subject line (optional).
        body:      Email body text (optional).

    Returns:
        JSON string with status and message.
    """
    from config import GMAIL_ADDRESS, GMAIL_APP_PASS

    if GMAIL_ADDRESS == "YOUR_GMAIL@gmail.com" or GMAIL_APP_PASS == "YOUR_APP_PASSWORD_HERE":
        return json.dumps({
            "status": "error",
            "message": (
                "Gmail credentials are not configured. "
                "Please set GMAIL_ADDRESS and GMAIL_APP_PASS in config.py. "
                "Get an App Password at https://myaccount.google.com/apppasswords"
            )
        })

    try:
        msg = MIMEMultipart()
        msg["From"]    = GMAIL_ADDRESS
        msg["To"]      = recipient
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(GMAIL_ADDRESS, GMAIL_APP_PASS)
            smtp.sendmail(GMAIL_ADDRESS, recipient, msg.as_string())

        return json.dumps({
            "status": "success",
            "message": f"Email sent successfully to {recipient}."
        })

    except smtplib.SMTPAuthenticationError:
        return json.dumps({
            "status": "error",
            "message": (
                "Gmail authentication failed. "
                "Make sure you're using a Google App Password, not your regular password. "
                "Generate one at https://myaccount.google.com/apppasswords"
            )
        })
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Failed to send email: {str(e)}"
        })
