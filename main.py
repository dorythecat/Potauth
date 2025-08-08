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

sys_random = random.SystemRandom()

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
    },
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "Authentication endpoints"
        },
        {
            "name": "Utility",
            "description": "Utility endpoints"
        },
        {
            "name": "Potatoes",
            "description": "Potato-related endpoints"
        }
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

USERS_DB = "potauth.db" # User database
POTATO_DB = "potatoes.db" # Potatoes database

ALGORITHM = "HS256" # Algorith for JWT to use to encode tokens
security = HTTPBearer()

@app.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    return RedirectResponse("/docs", status_code=301)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta if expires_delta else timedelta(minutes=30))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> str | HTTPException:
    """Get and validate the Authorization header token."""
    token = credentials.credentials if credentials else None
    if not token:
        return HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={ "WWW-Authenticate": "Bearer" },
        )
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return data['access_token']
    except InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={ "WWW-Authenticate": "Bearer" },
        )



def get_potato_code(img: Image) -> str:
    """Get the potato code from an image."""
    # Literally just an image hash lol
    pixel_data = list(img.resize((16, 16)).convert("L").getdata())
    avg_pixel = sum(pixel_data)/len(pixel_data)
    bits = "".join(['1' if (px >= avg_pixel) else '0' for px in pixel_data])
    hex_representation = str(hex(int(bits, 2)))[2:][::-1].upper()
    return hex_representation


def random_crop(img: Image, size: tuple[int, int] = (256, 256)) -> Image:
    """Randomly crop an image."""
    if img.size[0] < size[0] or img.size[1] < size[1]:
        return img.resize((size[0], size[1])) # If the image is undersized, just return a sized version of it
    start_corner = sys_random.randint(0, img.size[0] - size[0]), sys_random.randint(0, img.size[1] - size[1])
    return img.crop((start_corner[0], start_corner[1], start_corner[0] + size[0], start_corner[1] + size[1]))


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
          tags=["Authentication"],
          responses={
              401: { "model": ErrorMessage },
              404: { "model": ErrorMessage }
          })
async def login(username: str,
                favourite_potato: PotatoType,
                image: Annotated[bytes, File(description="Selected image")]) -> str | JSONResponse:
    """Login to the API."""
    if not os.path.exists(USERS_DB):
        return JSONResponse(status_code=401, content={ "message": "User does no exist." })

    with open(USERS_DB, "r") as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip().split(":")
            if line[0] != username:
                continue
            if line[1] != str(favourite_potato.value):
                return JSONResponse(status_code=401, content={ "message": "Incorrect login data." })
            if not os.path.exists("images/users"):
                os.mkdir("images/users")
            if not os.path.exists(f"images/users/{username}.webp"):
                return JSONResponse(status_code=404, content={ "message": "User does not exist." })

            # Check image
            if get_potato_code(Image.open(BytesIO(base64.b64decode(image)))) != line[2]:
                return JSONResponse(status_code=401, content={ "message": "Incorrect login data." })

            return create_access_token({"access_token": username})
    return JSONResponse(status_code=404, content={ "message": "User does not exist." })


@app.post("/register",
          response_model=str,
          tags=["Authentication"],
          responses={
              401: { "model": ErrorMessage },
              404: { "model": ErrorMessage }
          })
async def register(username: str,
                   favourite_potato: PotatoType,
                   image: Annotated[bytes, File(description="Selected image")]) -> str | JSONResponse:
    """Register a new user."""
    if os.path.exists(USERS_DB):
        with open(USERS_DB, "r") as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip().split(":")
                if line[0] == username:
                    return JSONResponse(status_code=401, content={ "message": "User already exists." })
    img = Image.open(BytesIO(base64.b64decode(image)))
    img = random_crop(img)
    potato_code = get_potato_code(img)
    with open(USERS_DB, "a+") as f:
        f.write(f"\n{username}:{favourite_potato.value}:{potato_code}")
    img.save(f"images/users/{username}.webp")
    return create_access_token({"access_token": username})


@app.delete("/delete_user",
            tags=["Authentication"])
async def delete_user(token: str = Depends(get_current_token)) -> None:
    """Delete a user."""
    if not os.path.exists(USERS_DB):
        return # We don't need to do nothing
    with open(USERS_DB, "r") as f:
        lines = f.readlines()
    with open(USERS_DB, "w") as f:
        for line in lines:
            if line.strip().split(":")[0] != token:
                f.write(line)
    os.remove(f"images/users/{token}.webp")


@app.post("/add_fodder",
          tags=["Utility"])
async def add_fodder(image: Annotated[bytes, File(description="The image to send.")]) -> None:
    """Send a potato to the API, that will be added to the fodder list."""
    # Check the max fodder ID
    if not os.path.exists("images/fodder"):
        os.mkdir("images/fodder")
    if not os.path.exists("images/fodder/fodder_id"):
        with open("images/fodder/fodder_id", "w+") as f:
            f.write("0")

    with open("images/fodder/fodder_id", "r") as f:
        fodder_id = int(f.read().strip())

    # Open the image
    img = Image.open(BytesIO(image))
    for i in range(10):
        # Randomly crop 10 times and save the cropped versions
        img = random_crop(img)
        img.save(f"images/fodder/{fodder_id}_{i}" + ".webp")

    with open("images/fodder/fodder_id", "w") as f:
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
         response_model=Images,
         responses={
             404: { "model": ErrorMessage }
         },
         tags=["Utility"])
async def get_images(username: str) -> Images | JSONResponse:
    """Get a list of images, eight fodder, one the user image."""
    if not os.path.exists("images/fodder"):
        return JSONResponse(status_code=404, content={ "message": "There are no fodder images available." })
    if not (os.path.exists("images/users") and os.path.exists(f"images/users/{username}.webp")):
        return JSONResponse(status_code=404, content={ "message": "Tha user does not exist." })
    with open("images/fodder/fodder_id", "r") as f:
        fodder_id = int(f.read().strip())

    images = []
    while len(images) < 8:
        images.append(get_image_bytes(f"images/fodder/{sys_random.randint(0, fodder_id - 1)}_{sys_random.randint(0, 9)}.webp"))
    images.append(get_image_bytes(f"images/users/{username}.webp"))
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


@app.get("/potatoes/{username}",
         response_model=list[bytes],
         tags=["Potatoes"])
async def get_posts(username: str) -> list[bytes]:
    """Get all potatoes in your gallery."""
    if not os.path.exists(POTATO_DB):
        return []
    with open(POTATO_DB, "r") as f:
        lines = f.readlines()
    posts = []
    for line in lines:
        line = line.strip().split(":")
        if line[0] != username:
            continue
        img = Image.open(f"images/posts/{line[1]}.webp")
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='WEBP')
        posts.append(base64.b64encode(img_byte_arr.getvalue()))
    return posts


@app.post("/post",
          tags=["Potatoes"])
async def post(token: Annotated[str, Depends(get_current_token)],
               image: Annotated[bytes, File(description="The image to send.")],) -> None:
    """Post a potato to your gallery."""
    if not os.path.exists("images/posts"):
        os.mkdir("images/posts")
    img = Image.open(BytesIO(base64.b64decode(image)))
    potato_code = get_potato_code(img)
    img.save(f"images/posts/{potato_code}.webp")
    with open(POTATO_DB, "a+") as f:
        f.write(f"\n{token}:{potato_code}")


@app.delete("/delete_post",
            tags=["Potatoes"])
async def del_post(token: Annotated[str, Depends(get_current_token)],
                   image: Annotated[bytes, File(description="The image to send.")]) -> None:
    """Delete a potato from your gallery."""
    if not os.path.exists("images/posts"):
        return
    potato_code = get_potato_code(Image.open(BytesIO(base64.b64decode(image))))
    os.remove(f"images/posts/{potato_code}.webp")
    with open(POTATO_DB, "r") as f:
        lines = f.readlines()
    with open(POTATO_DB, "w") as f:
        for line in lines:
            if line.strip().split(":")[1] == potato_code:
                continue
            f.write(line)