from datetime import datetime
from sqlalchemy.sql.sqltypes import Date
from app.config import settings
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Format DOB from MM / DD / YYYY (str) -> YYYY-MM-DD (Date)
def format_dob(dob_str: str) -> Date:
    dob_date = datetime.strptime(dob_str, "%m / %d / %Y").date()
    return dob_date

# Format DOB from YYYY-MM-DD (Date) -> MM / DD / YYYY (str)
def format_dob_str(dob_date: Date) -> str:
    dob_str = dob_date.strftime("%m / %d / %Y")
    return dob_str

# Send email to developer
def send_email(subject: str, message: str, pictures: list[str] = None) -> bool:
    msg = MIMEMultipart()
    msg['From'] = settings.developer_email
    msg['To'] = settings.developer_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message + f'\nPictures: {pictures}', 'plain'))

    try:
        server = smtplib.SMTP_SSL('smtp.sendgrid.net', 465)
        server.login('apikey', settings.sendgrid_api_key)
        server.sendmail(settings.developer_email, settings.developer_email, msg.as_string())
        server.close()
        return True
    except Exception as e:
        print(e)
        return False