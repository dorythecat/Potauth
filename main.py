from enum import Enum
from typing import Annotated

import jwt
import random
import os
import base64

from fastapi import Depends, FastAPI, HTTPException, Security, Body, Response, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from jwt import InvalidTokenError

from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

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

DATABASE_PATH = "potauth.db"

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



def get_potato_code(img_byte_arr: bytes) -> int:
    """Get the potato code from an image."""
    return int(''.join(img_byte_arr.hex().translate(''.maketrans('abcdef', '192837')).split("0"))[::-1][:4300]) % 9007199254740991


class ErrorMessage(BaseModel):
    message: str


class PotatoType(str, Enum):
    fried = "fried"
    baked = "baked"
    stuffed = "stuffed"
    mashed = "mashed"
    salted = "salted"
    roasted = "roasted"
    raw = "raw"


@app.post("/login",
          response_model=str,
          responses={
              401: {"model": ErrorMessage},
              404: {"model": ErrorMessage}
          })
def login(username: str,
          favourite_potato: PotatoType,
          potato_code: int,
          image: Annotated[bytes, File(description="Selected image")]) -> str | JSONResponse:
    """Login to the API."""
    if not os.path.exists(DATABASE_PATH):
        return JSONResponse(status_code=401, content={"message": "User does no exist."})

    with open(DATABASE_PATH, "r") as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip().split(":")
            if line[0] != username:
                continue
            if line[1] != str(favourite_potato.value) or line[2] != str(potato_code):
                return JSONResponse(status_code=401, content={"message": "Incorrect login data."})
            if not os.path.exists("images/users"):
                os.mkdir("images/users")
            if not os.path.exists(f"images/users/{username}.webp"):
                return JSONResponse(status_code=404, content={"message": "User does not exist."})

            # Check image
            img = Image.open(BytesIO(image))
            img_byte_arr = BytesIO()
            img.save(img_byte_arr, format='WEBP')
            potato_code = get_potato_code(img_byte_arr.getvalue())

            if potato_code != int(line[2]):
                return JSONResponse(status_code=401, content={"message": "Incorrect potato."})

            return create_access_token({"access_token": username})
    return JSONResponse(status_code=404, content={"message": "User does not exist."})


class RegisterResponse(BaseModel):
    access_token: str
    potato_code: int


@app.post("/register",
          response_model=RegisterResponse,
          responses={
              401: {"model": ErrorMessage},
              404: {"model": ErrorMessage}
          })
def register(username: str,
             favourite_potato: PotatoType,
             image: Annotated[bytes, File(description="Selected image")]) -> RegisterResponse | JSONResponse:
    """Register a new user."""
    img = Image.open(BytesIO(image))
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='WEBP')
    potato_code = get_potato_code(img_byte_arr.getvalue())

    if os.path.exists(DATABASE_PATH):
        with open(DATABASE_PATH, "r") as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip().split(":")
                if line[0] == username:
                    return JSONResponse(status_code=401, content={"message": "User already exists."})
        with open(DATABASE_PATH, "a+") as f:
            f.write(f"\n{username}:{favourite_potato.value}:{potato_code}")
            img = Image.open(BytesIO(image))
            img.save(f"images/users/{username}.webp")
            return RegisterResponse(access_token=create_access_token({"access_token": username}),
                                    potato_code=potato_code)
    else:
        with open(DATABASE_PATH, "w+") as f:
            f.write(f"{username}:{favourite_potato.value}:{potato_code}")
            img = Image.open(BytesIO(image))
            img.save(f"images/users/{username}.webp")
            return RegisterResponse(access_token=create_access_token({"access_token": username}),
                                    potato_code=potato_code)


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


class Images(BaseModel):
    image0: Annotated[bytes, File()]
    image1: Annotated[bytes, File()]
    image2: Annotated[bytes, File()]
    image3: Annotated[bytes, File()]
    image4: Annotated[bytes, File()]
    image5: Annotated[bytes, File()]
    image6: Annotated[bytes, File()]
    image7: Annotated[bytes, File()]
    image8: Annotated[bytes, File()]


def get_image_bytes(image: str) -> bytes:
    """Get the image bytes from the image string."""
    img = Image.open(image)
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='WEBP')
    return base64.b64encode(img_byte_arr.getvalue())


@app.get("/get_images",
         response_model=Images)
async def get_images(username: str) -> Images:
    """Get a list of images, eight fodder, one the user image."""
    with open("images/fodder/fodder_id", "r") as f:
        fodder_id = int(f.read().strip())

    images = []
    while True:
        random_id = random.randint(0, fodder_id - 1)
        if random_id not in images:
            images.append(get_image_bytes(f"images/fodder/{random_id}_{random.randint(0, 9)}.webp"))
        if len(images) == 8:
            break
    images.append(f"images/users/{username}.webp")
    random.shuffle(images)

    return Images(
        image0=images[0],
        image1=images[1],
        image2=images[2],
        image3=images[3],
        image4=images[4],
        image5=images[5],
        image6=images[6],
        image7=images[7],
        image8=images[8],
    )


@app.put("/get_code")
async def get_code(image: Annotated[bytes, File(description="The image to get the code for.")]):
    """Gives you the potato code for your potato."""
    img = Image.open(BytesIO(image))
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='WEBP')
    return get_potato_code(img_byte_arr.getvalue())

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