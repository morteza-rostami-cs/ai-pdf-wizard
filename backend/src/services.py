from email.message import EmailMessage
import aiosmtplib
from datetime import datetime, timezone, timedelta
from jose import jwt, JWTError
from fastapi import HTTPException, status, Request

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


# generate jwt
def generate_jwt(
    payload: Dictor,
    expires_minutes: int = settings.JWT_EXPIRE_MINS,
):
  """ create jwt token with expiration date """

  # set expiration date
  expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)

  # add expiration date to payload
  payload.update({"exp": expire})

  # generate jwt token
  token = jwt.encode(
    claims=payload,
    key=settings.JWT_SECRET_KEY , # jwt secret
    algorithm=settings.JWT_ALGORITHM,
  )

  return token

# verify jwt

def verify_jwt(token: str) -> Dictor:
  """
  verify jwt and return decoded token
  raise 401 -> if invalid or expired
  """

  try:
    decoded = jwt.decode(
      token=token, 
      key=settings.JWT_SECRET_KEY,
      algorithms=[settings.JWT_ALGORITHM],
    )

    return decoded

  except JWTError:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid or expired token")
  

# can verify token
def verify_token(request: Request) -> Dictor | None:
  """ takes request, validate token """

  token = request.cookies.get("access_token")

  if not token:
    print("no token")
    return None
  
  payload = verify_jwt(token=token)

  if not payload:
    print('no payload')
    return None
  
  return payload