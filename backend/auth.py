import hashlib
import secrets
from datetime import datetime, timedelta

from jose import jwt

from database import get_connection


SECRET_KEY = "food20_super_secret_key_change_later"
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60 * 24


# -----------------------------
# Password hashing
# -----------------------------

def hash_password(password):

    salt = secrets.token_bytes(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        100000
    )

    return salt.hex() + ":" + password_hash.hex()


def verify_password(password, stored_hash):

    try:
        salt_hex, hash_hex = stored_hash.split(":")

        salt = bytes.fromhex(salt_hex)

        password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            100000
        )

        return secrets.compare_digest(
            password_hash.hex(),
            hash_hex
        )

    except Exception:
        return False


# -----------------------------
# Create user
# -----------------------------

def create_user(username, email, password):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT user_id
        FROM users
        WHERE username = ? OR email = ?
        """,
        (username, email)
    )

    existing_user = cursor.fetchone()

    if existing_user:
        cursor.close()
        connection.close()
        return None

    password_hash = hash_password(password)

    cursor.execute(
        """
        INSERT INTO users
        (
            username,
            email,
            password_hash
        )
        VALUES (?, ?, ?)
        """,
        (
            username,
            email,
            password_hash
        )
    )

    connection.commit()

    user_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return user_id


# -----------------------------
# Login
# -----------------------------

def authenticate_user(username, password):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            user_id,
            username,
            email,
            password_hash
        FROM users
        WHERE username = ?
        """,
        (username,)
    )

    user = cursor.fetchone()

    cursor.close()
    connection.close()

    if user is None:
        return None

    user_id, username, email, password_hash = user

    if not password_hash:
        return None

    if not verify_password(
        password,
        password_hash
    ):
        return None

    return {
        "user_id": user_id,
        "username": username,
        "email": email
    }


# -----------------------------
# JWT token
# -----------------------------

def create_access_token(user_id, username):

    expire = datetime.utcnow() + timedelta(
        minutes=TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "user_id": user_id,
        "username": username,
        "exp": expire
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )