"""JWT token create / decode / revoke (with blacklist)."""
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt

from app.core.config import settings

# In-memory blacklist (swap for Redis in production)
_blacklisted_jtis: set[str] = set()


def _now() -> datetime:
    return datetime.now(timezone.utc)


# ── Token creation ─────────────────────────────────────────
def _create_token(
    subject: str,
    token_type: str,
    secret: str,
    expire_delta: timedelta,
    extra_claims: Optional[dict] = None,
) -> str:
    jti = f"{subject}-{token_type}-{_now().timestamp()}-{os.urandom(4).hex()}"
    payload = {
        "sub":  str(subject),
        "type": token_type,
        "jti":  jti,
        "iat":  _now(),
        "exp":  _now() + expire_delta,
        **(extra_claims or {}),
    }
    return jwt.encode(payload, secret, algorithm=settings.JWT_ALGORITHM)


def create_access_token(user_id: int, role: str) -> str:
    return _create_token(
        subject=user_id,
        token_type="access",
        secret=settings.JWT_SECRET_KEY,
        expire_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MIN),
        extra_claims={"role": role},
    )


def create_refresh_token(user_id: int) -> str:
    return _create_token(
        subject=user_id,
        token_type="refresh",
        secret=settings.JWT_REFRESH_SECRET,
        expire_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


# ── Token decoding ─────────────────────────────────────────
def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except JWTError as e:
        raise JWTError(f"Invalid access token: {e}")

    if payload.get("type") != "access":
        raise JWTError("Token is not an access token")
    if payload.get("jti") in _blacklisted_jtis:
        raise JWTError("Token has been revoked")
    return payload


def decode_refresh_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_REFRESH_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except JWTError as e:
        raise JWTError(f"Invalid refresh token: {e}")

    if payload.get("type") != "refresh":
        raise JWTError("Token is not a refresh token")
    if payload.get("jti") in _blacklisted_jtis:
        raise JWTError("Token has been revoked")
    return payload


# ── Blacklisting (logout / revoke) ─────────────────────────
def _revoke(token: str, secret: str) -> None:
    try:
        payload = jwt.decode(token, secret, algorithms=[settings.JWT_ALGORITHM])
        jti = payload.get("jti")
        if jti:
            _blacklisted_jtis.add(jti)
    except JWTError:
        pass


def revoke_access_token(token: str) -> None:
    _revoke(token, settings.JWT_SECRET_KEY)


def revoke_refresh_token(token: str) -> None:
    _revoke(token, settings.JWT_REFRESH_SECRET)


def is_blacklisted(jti: str) -> bool:
    return jti in _blacklisted_jtis


# Need os for random hex
import os
