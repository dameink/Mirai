import hashlib
import hmac
import secrets


# Number of PBKDF2 iterations.
# Good for the current prototype and easy to increase later.
PBKDF2_ITERATIONS = 310_000


def hash_password(password: str) -> str:
    """
    Securely hash a password using PBKDF2-HMAC-SHA256.

    Stored format:
        iterations$salt$hash
    """

    salt = secrets.token_hex(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PBKDF2_ITERATIONS,
    ).hex()

    return f"{PBKDF2_ITERATIONS}${salt}${password_hash}"


def verify_password(password: str, stored_hash: str) -> bool:
    """
    Verify a password against the stored PBKDF2 hash.
    """

    try:
        iterations, salt, expected_hash = stored_hash.split("$")
        iterations = int(iterations)

        actual_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            iterations,
        ).hex()

        return hmac.compare_digest(actual_hash, expected_hash)

    except (ValueError, TypeError):
        return False


def create_token() -> str:
    """
    Generate a cryptographically secure random token.
    """

    return secrets.token_urlsafe(48)