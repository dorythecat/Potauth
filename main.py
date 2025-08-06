from typing import Annotated

import jwt
import random
import os

from fastapi import Depends, FastAPI, HTTPException, Security, Body, Response, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone

from PIL import Image
from io import BytesIO

from starlette.responses import RedirectResponse

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

@app.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    return RedirectResponse("/docs", status_code=301)


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


@app.put("/add_fodder")
async def add_fodder(image: Annotated[bytes, File(description="The image to send.")]):
    """Send a potato to the API, that will be added to the fodder list."""
    # Check the max fodder ID
    if not os.path.exists("images/fodder/fodder_id"):
        with open("images/fodder/fodder_id", "w+") as f:
            f.write("0")

    with open("images/fodder/fodder_id", "r") as f:
        fodder_id = int(f.read().strip())

    # Open the image
    img = Image.open(BytesIO(image))
    for i in range(10):
        # Randomly crop 10 times and save the cropped versions
        start_corner = random.randint(0, img.size[0] - 256), random.randint(0, img.size[1] - 256)
        cropped_img = img.crop((start_corner[0], start_corner[1], start_corner[0] + 256, start_corner[1] + 256))
        cropped_img.save(f"images/fodder/{fodder_id}_{i}" + ".webp")

    with open("images/fodder/fodder_id", "w+") as f:
        f.write(str(fodder_id + 1))


@app.put("/get_code")
async def get_code(image: Annotated[bytes, File(description="The image to send.")]):
    """Gives you the potato code for your potato."""
    img = Image.open(BytesIO(image))
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='WEBP')
    img_byte_arr = img_byte_arr.getvalue()
    processed = ''.join(img_byte_arr.hex().translate(''.maketrans('abcdef', '192837')).split("0"))
    return str(int(processed[::-1][:4300]) % 9007199254740991)

@app.get("/testpotato",
         responses = {
             200: { "content": {"image/webp": {}}}
         },
         response_class=Response
)
async def get_image():
    img = Image.open('testpotato.png', mode='r')
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='WEBP')
    img_byte_arr = img_byte_arr.getvalue()

    # media_type here sets the media type of the actual response sent to the client.
    return Response(content=img_byte_arr, media_type="image/webp")