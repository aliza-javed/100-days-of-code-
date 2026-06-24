"""FastAPI dependencies: auth + role guards."""
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError

from app.core.tokens import decode_access_token
from app.services.store import get_user

bearer_scheme = HTTPBearer(auto_error=False)

_401 = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Not authenticated",
    headers={"WWW-Authenticate": "Bearer"},
)
_403 = HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)]
) -> dict:
    if not credentials:
        raise _401
    try:
        payload = decode_access_token(credentials.credentials)
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = int(payload["sub"])
    user = get_user(user_id)
    if not user:
        raise _401
    if not user.get("is_active", True):
        raise HTTPException(403, "Account is deactivated")
    return user


def require_role(role: str):
    def _check(current: Annotated[dict, Depends(get_current_user)]) -> dict:
        if current.get("role") != role:
            raise _403
        return current
    return _check


def require_roles(roles: list[str]):
    def _check(current: Annotated[dict, Depends(get_current_user)]) -> dict:
        if current.get("role") not in roles:
            raise _403
        return current
    return _check


# Convenience aliases
AdminOnly  = Depends(require_role("admin"))
EditorPlus = Depends(require_roles(["admin", "editor"]))
AnyUser    = Depends(get_current_user)
