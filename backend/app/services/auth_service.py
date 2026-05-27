import os

from datetime import (

    datetime,

    timedelta
)

from jose import jwt

from passlib.context import (
    CryptContext
)

from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

SECRET_KEY = os.getenv(
    "SECRET_KEY"
)

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_HOURS = 24

pwd_context = CryptContext(

    schemes=["bcrypt"],

    deprecated="auto"
)

# ─────────────────────────────────────────────
# HASH PASSWORD
# ─────────────────────────────────────────────

def hash_password(

    password: str
):

    return pwd_context.hash(
        password
    )

# ─────────────────────────────────────────────
# VERIFY PASSWORD
# ─────────────────────────────────────────────

def verify_password(

    plain_password: str,

    hashed_password: str
):

    return pwd_context.verify(

        plain_password,

        hashed_password
    )

# ─────────────────────────────────────────────
# CREATE ACCESS TOKEN
# ─────────────────────────────────────────────

def create_access_token(

    data: dict
):

    to_encode = data.copy()

    expire = (

        datetime.utcnow()
        + timedelta(
            hours=
            ACCESS_TOKEN_EXPIRE_HOURS
        )
    )

    to_encode.update({

        "exp": expire
    })

    encoded_jwt = jwt.encode(

        to_encode,

        SECRET_KEY,

        algorithm=ALGORITHM
    )

    return encoded_jwt