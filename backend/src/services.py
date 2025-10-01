from email.message import EmailMessage
import aiosmtplib

# my imports 
from src.dtos import TaskTypes, Dictor
from src.models import Task
from src.config import settings

# fire tasks 
async def fire_task(
    task_type: TaskTypes,
    payload: Dictor,
) -> Task:
  """ 
  store a task in mongodb
  args: task_type and payload data 
  """

  task = Task(
    task_type= task_type,
    payload=payload
  )

  await task.insert()

  return task

# send email (smtp gmail)

async def send_email(
    to_email: str,  # receiver
    subject: str, # email subject
    body: str, # email content
):

  smtp_email = settings.SMTP_FROM
  smtp_port = settings.SMTP_PORT
  smtp_host = settings.SMTP_HOST # name of service or my_gmail
  smtp_password = settings.SMTP_PASS
  
  # email message template
  message = EmailMessage()

  message['From'] = smtp_email
  # user email
  message["To"] = to_email
  message['subject'] = subject
  # email  content
  message.set_content(body) 

  # send the email
  await aiosmtplib.send(
    message,
    hostname=smtp_host,
    port=smtp_port,
    start_tls=True,
    username=smtp_email, # my_gmail
    password=smtp_password,
  )

  print(f"email send to: {to_email}")

