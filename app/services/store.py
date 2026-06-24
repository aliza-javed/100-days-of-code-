"""In-memory user store (swap for SQLAlchemy/PostgreSQL in production)."""
from datetime import datetime, timezone
from typing import Optional

from app.core.security import hash_password, verify_password

_users: dict[int, dict] = {}
_counter: int = 0


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_user(username: str, email: str, password: str,
                full_name: str, role: str = "viewer") -> dict:
    global _counter
    _counter += 1
    record = {
        "id":         _counter,
        "username":   username.lower(),
        "email":      email.lower(),
        "hashed_pw":  hash_password(password),
        "full_name":  full_name,
        "role":       role,
        "is_active":  True,
        "created_at": _now(),
    }
    _users[_counter] = record
    return _safe(record)


def get_user(uid: int) -> Optional[dict]:
    u = _users.get(uid)
    return _safe(u) if u else None


def get_user_by_username(username: str) -> Optional[dict]:
    """Returns the FULL record including hashed_pw (internal use only)."""
    for u in _users.values():
        if u["username"] == username.lower():
            return u
    return None


def get_user_by_email(email: str) -> Optional[dict]:
    for u in _users.values():
        if u["email"] == email.lower():
            return u
    return None


def get_all_users() -> list[dict]:
    return [_safe(u) for u in _users.values()]


def authenticate_user(username: str, password: str) -> Optional[dict]:
    """Verify credentials — returns safe user dict or None."""
    user = get_user_by_username(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_pw"]):
        return None
    return _safe(user)


def update_password(uid: int, new_password: str) -> bool:
    if uid not in _users:
        return False
    _users[uid]["hashed_pw"] = hash_password(new_password)
    return True


def deactivate_user(uid: int) -> bool:
    if uid not in _users:
        return False
    _users[uid]["is_active"] = False
    return True


def _safe(u: dict) -> dict:
    """Strip sensitive fields before returning to caller."""
    return {k: v for k, v in u.items() if k != "hashed_pw"}
