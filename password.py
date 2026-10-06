import hashlib
import os
import base64


def hash_password(password):
    salt = os.urandom(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        100000
    )

    salt_encoded = base64.b64encode(salt).decode("utf-8")
    hash_encoded = base64.b64encode(password_hash).decode("utf-8")

    return salt_encoded + ":" + hash_encoded


def verify_password(password, stored_hash):
    try:
        salt_encoded, hash_encoded = stored_hash.split(":")

        salt = base64.b64decode(salt_encoded)
        stored_password_hash = base64.b64decode(hash_encoded)

        password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            100000
        )

        return password_hash == stored_password_hash

    except (ValueError, TypeError):
        return False