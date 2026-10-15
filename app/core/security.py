from passlib.context import CryptContext

# Create a CryptContext object, using the bcrypt hashing algorithm.
# "deprecated=auto" allows passlib to handle older hashes securely if we ever update algorithms.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """
    Takes a plain-text password and returns a secure, one-way bcrypt hash.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Takes a plain-text password and verifies it against the stored bcrypt hash.
    Returns True if they match, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)

import hashlib

def get_token_hash(token: str) -> str:
    """
    Creates a SHA-256 hash of a token.
    Useful for safely storing tokens (like refresh tokens) in the database.
    """
    return hashlib.sha256(token.encode()).hexdigest()

