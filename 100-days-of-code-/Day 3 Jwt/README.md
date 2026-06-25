# Day 3 — JWT Authentication with FastAPI

Part of my [#100DaysOfCode](../100-days-of-code.md) challenge — built on top of [Day 2](../day02-fastapi/).

Full JWT auth system: register → login → access/refresh tokens → role-based guards → logout with blacklisting.

## Auth flow

```
Register ──► Login ──► Access Token (30 min) ──► Protected Routes
                  └──► Refresh Token (7 days) ──► /auth/refresh ──► New Access Token
                                                        (old refresh token revoked)
Logout ──► Access token blacklisted ──► 401 on reuse
```

## Project structure

```
app/
├── main.py
├── core/
│   ├── config.py          # JWT secrets, expiry settings
│   ├── security.py        # PBKDF2 password hashing + verification
│   ├── tokens.py          # create / decode / revoke JWT tokens
│   └── deps.py            # FastAPI dependency injection + role guards
├── schemas/auth.py        # Pydantic models for all auth flows
├── services/store.py      # In-memory user store (swap with ORM)
└── api/v1/endpoints/
    ├── auth.py            # /auth/* endpoints
    └── users.py           # /api/v1/users/* (role-protected)
tests/
└── test_auth.py           # 26 tests — all passing
```

## Endpoints

### Auth  `/auth`
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/register` | ❌ | Create account |
| POST | `/login` | ❌ | Get access + refresh tokens |
| POST | `/refresh` | Refresh token | Rotate refresh → new access token |
| POST | `/logout` | Bearer | Blacklist access token |
| GET  | `/me` | Bearer | Get own profile |
| POST | `/change-password` | Bearer | Change own password |

### Users  `/api/v1/users`
| Method | Path | Required role | Description |
|--------|------|--------------|-------------|
| GET | `/` | admin | List all users |
| GET | `/me` | any | Own profile |
| GET | `/{id}` | admin, editor | Get user by ID |
| DELETE | `/{id}` | admin | Deactivate user |

## Security features

| Feature | Implementation |
|---|---|
| Password hashing | PBKDF2-HMAC-SHA256, 260k iterations, 32-byte random salt |
| Access token | HS256 JWT, 30-minute expiry, carries `sub` + `role` + `jti` |
| Refresh token | Separate HS256 JWT, 7-day expiry, single-use (rotated on use) |
| Token blacklist | In-memory JTI set (swap for Redis in production) |
| Role-based access | `require_role()` + `require_roles()` dependency factories |
| No credential enumeration | Wrong username and wrong password return identical 401 |
| Cross-field validation | Age ↔ DOB, same-as-current password check |

## Quick start

```bash
git clone https://github.com/aliza-javed/100-days-of-code.git
cd 100-days-of-code/day03-jwt
pip install -r requirements.txt
uvicorn app.main:app --reload
# Open http://localhost:8000/docs
pytest tests/ -v
```

## What I learned today

- `python-jose` vs `PyJWT` — jose handles algorithm confusion attacks better out of the box
- JTI (JWT ID) claim is the right way to blacklist individual tokens without invalidating all sessions
- Refresh token rotation: revoke the old one on use, issue a new one — limits the damage of a stolen refresh token
- `Depends()` factories (`require_role`, `require_roles`) keep endpoint code clean with zero duplication
- PBKDF2 with 260k iterations is NIST-recommended for SHA-256 — bcrypt is still preferred when available
