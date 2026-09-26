"""
PrivacyLens – Password hashing using passlib + bcrypt.
Never store or log plain-text passwords.
"""
import warnings
import logging
# Suppress passlib/bcrypt version-detection warning (cosmetic only, does not affect security)
logging.getLogger("passlib").setLevel(logging.ERROR)
warnings.filterwarnings("ignore", message=".*bcrypt.*")

from passlib.context import CryptContext

# bcrypt with 12 rounds — strong enough for production, fast enough for demos
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


def hash_password(plain_password: str) -> str:
    """Return a bcrypt hash of the plain-text password."""
    return _pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return True if plain_password matches the stored hash."""
    return _pwd_context.verify(plain_password, hashed_password)
