from typing import Annotated

import jwt

from fastapi import Depends, FastAPI, HTTPException, Security, Body, Response, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone

from PIL import Image
from io import BytesIO

app = FastAPI(
    title="Potauth API",
    summary="The Potato-based authentication API",
    description="""
        The Potauth API allows users to authenticate themselves by using potatoes, in a variety of forms, including:
        - Fried potatoes
        - Baked potatoes
        - Stuffed potatoes
        - Mashed potatoes
        - And much more!
        
        Note: Potauth does not support sweet potatoes.
    """,
    version="1.0.0",
    license_info={
        "name": "GNU Affero General Public License v3.0 or later",
        "identifier": "AGPL-3.0-or-later"
    }
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_PATH = "potauth.db" # TODO

ALGORITHM = "HS256" # Algorith for JWT to use to encode tokens
security = HTTPBearer()

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> str | HTTPException:
    """Get and validate the Authorization header token."""
    token = credentials.credentials if credentials else None
    if not token:
        return None
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return data['access_token']
    except InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


class ErrorMessage(BaseModel):
    message: str


@app.get("/login",
         response_model=None,
         responses={
             401: {"model": ErrorMessage},
             403: {"model": ErrorMessage},
             404: {"model": ErrorMessage}
         })
def login(): # TODO
    """Login to the API."""
    return None


@app.put("/send_image")
async def send_image(image: Annotated[bytes, File(description="The image to send.")]):
    """Send an image to the API."""
    img = Image.open(BytesIO(image))
    img = img.crop((0, 0, 256, 256))
    img.save('test.png')


@app.get("/testpotato",
         responses = {
             200: { "content": {"image/png": {}}}
         },
         response_class=Response
)
async def get_image():
    img = Image.open('testpotato.png', mode='r')
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    # media_type here sets the media type of the actual response sent to the client.
    return Response(content=img_byte_arr, media_type="image/png")