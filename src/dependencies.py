from fastapi import Request, HTTPException, status, WebSocket
from jose import JWTError

# my imports
from src.models import User
from src.services import verify_jwt

# ========auth guard

async def auth_guard(request: Request) -> User:
  """ dependency -> protect auth routes """

  token = request.cookies.get("access_token")

  if not token:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="authentication required to access this route"
    )
  
  try:
    payload = verify_jwt(token=token)

    user_id = payload.get("user_id")

    user = await User.get(document_id=user_id)

    if not user or not user.is_active:
      raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid authentication"
      )

    # return user -> into our route
    return user
  except Exception:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="invalid or expired token"
    )

async def websocket_auth_guard(websocket: WebSocket):
  token = websocket.cookies.get("access_token")

  if not token:
    await websocket.close(code=1008)
    return
  
  try:
    payload = verify_jwt(token=token)

    user_id = payload.get("user_id")

    user = await User.get(document_id=user_id)

    if not user or not user.is_active:
      await websocket.close(code=1008)
      return

    # return user -> into our route
    return user
  except Exception:
    await websocket.close(code=1008)
    return


#=========guest guard

async def guest_guard(request: Request) -> None:
  """ dependency to block auth users from certain routes """

  token = request.cookies.get("access_token")

  if not token:
    return
  
  try: 
    payload = verify_jwt(token=token)

    user_id = payload.get("user_id")

    user = await User.get(document_id=user_id)

    if user:
      raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="already authenticated"
      )
    
  except JWTError:
    # token is expired or some how bad
    return

