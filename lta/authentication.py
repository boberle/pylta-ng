from dataclasses import dataclass

import firebase_admin.auth
from fastapi import HTTPException, Request
from firebase_admin._auth_utils import InvalidIdTokenError, UserDisabledError
from firebase_admin._token_gen import (
    CertificateFetchError,
    ExpiredIdTokenError,
    RevokedIdTokenError,
)

from lta.api.configuration import get_firebase_app


@dataclass
class AuthenticatedUser:
    id: str
    email_address: str
    is_admin: bool = False


def get_authenticated_user(request: Request) -> AuthenticatedUser:
    if "Authorization" not in request.headers:
        raise HTTPException(status_code=401, detail="Authorization header required")

    try:
        _, token = request.headers["Authorization"].split(maxsplit=1)
    except ValueError:
        raise HTTPException(
            status_code=403, detail="Illegal Authorization header format"
        )

    app = get_firebase_app()
    try:
        claims = firebase_admin.auth.verify_id_token(token, app=app)
    except (
        ValueError,
        InvalidIdTokenError,
        ExpiredIdTokenError,
        RevokedIdTokenError,
        CertificateFetchError,
        UserDisabledError,
    ):
        raise HTTPException(status_code=403, detail="Invalid or expired token")

    # example of claims:
    # {'iss': 'https://securetoken.google.com/testalpenglow', 'aud': 'testalpenglow', 'auth_time': 1724887049, 'user_id': 'aoroQmmmTkcSUPlXpp87TkiQIyG3', 'sub': 'aoroQmmmTkcSUPlXpp87TkiQIyG3', 'iat': 1724917110, 'exp': 1724920710, 'email': 'foobar@gmail.com', 'email_verified': False, 'firebase': {'identities': {'email': ['foobar@gmail.com']}, 'sign_in_provider': 'password'}, 'uid': 'aoroQmmmTkcSUPlXpp87TkiQIyG3'}
    return AuthenticatedUser(
        id=claims["uid"],
        email_address=claims["email"],
        is_admin=claims.get("admin", False),
    )


def get_admin_user(request: Request) -> AuthenticatedUser:
    user = get_authenticated_user(request)
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Unauthorized access")

    return user
