"""22 tests covering the full auth flow."""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import store
from app.core.tokens import _blacklisted_jtis

client = TestClient(app)


# ── Fixtures ───────────────────────────────────────────────────
@pytest.fixture(autouse=True)
def reset_store():
    store._users.clear()
    store._counter = 0
    _blacklisted_jtis.clear()
    yield


ADMIN = {
    "username": "admin_user", "email": "admin@test.com",
    "password": "Admin@1234", "full_name": "Admin User", "role": "admin",
}
EDITOR = {
    "username": "editor_user", "email": "editor@test.com",
    "password": "Editor@1234", "full_name": "Editor User", "role": "editor",
}
VIEWER = {
    "username": "viewer_user", "email": "viewer@test.com",
    "password": "Viewer@1234", "full_name": "Viewer User", "role": "viewer",
}


def _reg(data: dict) -> dict:
    r = client.post("/auth/register", json=data)
    assert r.status_code == 201, r.text
    return r.json()


def _login(username: str, password: str) -> dict:
    r = client.post("/auth/login", json={"username": username, "password": password})
    assert r.status_code == 200, r.text
    return r.json()


def _hdr(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ── Health ─────────────────────────────────────────────────────
class TestHealth:
    def test_root(self):
        r = client.get("/")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

    def test_health(self):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "healthy"


# ── Register ───────────────────────────────────────────────────
class TestRegister:
    def test_register_success(self):
        body = _reg(ADMIN)
        assert body["username"] == "admin_user"
        assert "password" not in body
        assert "hashed_pw" not in body

    def test_duplicate_username(self):
        _reg(ADMIN)
        r = client.post("/auth/register", json={**ADMIN, "email": "other@test.com"})
        assert r.status_code == 409

    def test_duplicate_email(self):
        _reg(ADMIN)
        r = client.post("/auth/register", json={**ADMIN, "username": "other_admin"})
        assert r.status_code == 409

    def test_weak_password(self):
        r = client.post("/auth/register", json={**VIEWER, "password": "weakpass"})
        assert r.status_code == 422

    def test_invalid_username(self):
        r = client.post("/auth/register", json={**VIEWER, "username": "bad user!"})
        assert r.status_code == 422


# ── Login ──────────────────────────────────────────────────────
class TestLogin:
    def test_login_success(self):
        _reg(ADMIN)
        tokens = _login(ADMIN["username"], ADMIN["password"])
        assert "access_token"  in tokens
        assert "refresh_token" in tokens
        assert tokens["token_type"] == "bearer"
        assert tokens["expires_in"] == 1800

    def test_wrong_password(self):
        _reg(ADMIN)
        r = client.post("/auth/login", json={"username": ADMIN["username"], "password": "Wrong@999"})
        assert r.status_code == 401

    def test_wrong_username(self):
        r = client.post("/auth/login", json={"username": "nobody", "password": "Pass@123"})
        assert r.status_code == 401

    def test_no_enumeration(self):
        """Same error for wrong user and wrong password."""
        _reg(ADMIN)
        r1 = client.post("/auth/login", json={"username": "nobody",          "password": "Pass@123"})
        r2 = client.post("/auth/login", json={"username": ADMIN["username"], "password": "WrongPass@1"})
        assert r1.json()["detail"] == r2.json()["detail"]


# ── Protected routes ───────────────────────────────────────────
class TestProtected:
    def test_me_authenticated(self):
        _reg(ADMIN)
        tokens = _login(ADMIN["username"], ADMIN["password"])
        r = client.get("/auth/me", headers=_hdr(tokens["access_token"]))
        assert r.status_code == 200
        assert r.json()["username"] == "admin_user"

    def test_me_no_token(self):
        r = client.get("/auth/me")
        assert r.status_code == 401

    def test_me_bad_token(self):
        r = client.get("/auth/me", headers=_hdr("not.a.real.jwt"))
        assert r.status_code == 401

    def test_admin_list_users(self):
        _reg(ADMIN)
        tokens = _login(ADMIN["username"], ADMIN["password"])
        r = client.get("/api/v1/users/", headers=_hdr(tokens["access_token"]))
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_viewer_cannot_list_users(self):
        _reg(VIEWER)
        tokens = _login(VIEWER["username"], VIEWER["password"])
        r = client.get("/api/v1/users/", headers=_hdr(tokens["access_token"]))
        assert r.status_code == 403

    def test_editor_can_get_user_by_id(self):
        _reg(ADMIN)
        _reg(EDITOR)
        admin = _login(ADMIN["username"], ADMIN["password"])
        editor = _login(EDITOR["username"], EDITOR["password"])
        r = client.get("/api/v1/users/1", headers=_hdr(editor["access_token"]))
        assert r.status_code == 200


# ── Token refresh ──────────────────────────────────────────────
class TestRefresh:
    def test_refresh_success(self):
        _reg(ADMIN)
        tokens = _login(ADMIN["username"], ADMIN["password"])
        r = client.post("/auth/refresh", headers=_hdr(tokens["refresh_token"]))
        assert r.status_code == 200
        assert "access_token" in r.json()

    def test_refresh_token_rotated(self):
        """Old refresh token should fail after rotation."""
        _reg(ADMIN)
        tokens = _login(ADMIN["username"], ADMIN["password"])
        old_rt = tokens["refresh_token"]
        client.post("/auth/refresh", headers=_hdr(old_rt))
        r2 = client.post("/auth/refresh", headers=_hdr(old_rt))
        assert r2.status_code == 401

    def test_access_token_not_usable_as_refresh(self):
        _reg(ADMIN)
        tokens = _login(ADMIN["username"], ADMIN["password"])
        r = client.post("/auth/refresh", headers=_hdr(tokens["access_token"]))
        assert r.status_code == 401


# ── Logout ─────────────────────────────────────────────────────
class TestLogout:
    def test_logout_revokes_token(self):
        _reg(EDITOR)
        tokens = _login(EDITOR["username"], EDITOR["password"])
        at = tokens["access_token"]
        assert client.get("/auth/me", headers=_hdr(at)).status_code == 200
        assert client.post("/auth/logout", headers=_hdr(at)).status_code == 204
        assert client.get("/auth/me", headers=_hdr(at)).status_code == 401

    def test_logout_without_token(self):
        r = client.post("/auth/logout")
        assert r.status_code == 204


# ── Change password ────────────────────────────────────────────
class TestChangePassword:
    def test_change_password_success(self):
        _reg(VIEWER)
        tokens = _login(VIEWER["username"], VIEWER["password"])
        r = client.post(
            "/auth/change-password",
            json={"current_password": VIEWER["password"], "new_password": "NewViewer@999"},
            headers=_hdr(tokens["access_token"]),
        )
        assert r.status_code == 204
        new = _login(VIEWER["username"], "NewViewer@999")
        assert "access_token" in new

    def test_change_password_wrong_current(self):
        _reg(EDITOR)
        tokens = _login(EDITOR["username"], EDITOR["password"])
        r = client.post(
            "/auth/change-password",
            json={"current_password": "WrongPass@1", "new_password": "NewEditor@999"},
            headers=_hdr(tokens["access_token"]),
        )
        assert r.status_code == 400
