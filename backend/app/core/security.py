"""
Security & Cryptography Module
Implements JWT tokens, password hashing, and AES-256-GCM encryption for cloud provider credentials.
"""

import base64
import os
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

import jwt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.core.config import settings
from app.core.exceptions import AuthenticationFailedException


def _get_aes_key() -> bytes:
    """Derives a fixed 32-byte key from settings.SECRET_KEY for AES-256-GCM."""
    return hashlib.sha256(settings.SECRET_KEY.encode("utf-8")).digest()


def encrypt_secret(plain_text: str) -> str:
    """
    Encrypts sensitive text (e.g. AWS Secret Access Key, Azure Client Secret) using AES-256-GCM.
    Returns base64 encoded string containing IV (12 bytes) + Ciphertext + Tag (16 bytes).
    """
    if not plain_text:
        return ""
    key = _get_aes_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)  # 96-bit nonce
    ciphertext = aesgcm.encrypt(nonce, plain_text.encode("utf-8"), None)
    # Combine nonce + ciphertext
    combined = nonce + ciphertext
    return base64.b64encode(combined).decode("utf-8")


def decrypt_secret(cipher_b64: str) -> str:
    """Decrypts base64 encoded AES-256-GCM encrypted string."""
    if not cipher_b64:
        return ""
    try:
        combined = base64.b64decode(cipher_b64.encode("utf-8"))
        if len(combined) < 28:  # 12 bytes nonce + 16 bytes tag minimum
            raise ValueError("Invalid ciphertext length")
        nonce = combined[:12]
        ciphertext = combined[12:]
        key = _get_aes_key()
        aesgcm = AESGCM(key)
        decrypted = aesgcm.decrypt(nonce, ciphertext, None)
        return decrypted.decode("utf-8")
    except Exception as e:
        raise ValueError(f"Decryption failed: {str(e)}")


def hash_password(password: str, salt: Optional[bytes] = None) -> str:
    """Secure password hashing using PBKDF2-HMAC-SHA256 with 100,000 iterations."""
    if salt is None:
        salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
    return base64.b64encode(salt + key).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against stored PBKDF2 hash."""
    try:
        decoded = base64.b64decode(hashed_password.encode("utf-8"))
        salt = decoded[:16]
        stored_key = decoded[16:]
        computed_key = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt, 100000)
        return computed_key == stored_key
    except Exception:
        return False


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Generates a signed JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decodes and validates a JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailedException("Session token has expired. Please re-authenticate.")
    except jwt.InvalidTokenError:
        raise AuthenticationFailedException("Invalid authentication token format or signature.")
