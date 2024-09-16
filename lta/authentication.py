import re
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

HAS_SET_OWN_PASSWORD_FIELD = "hasSetOwnPassword"


@dataclass
class AuthenticatedUser:
    id: str
    email_address: str
    is_admin: bool = False


def get_authenticated_user(
    request: Request,
    allow_default_password_user: bool = False,
) -> AuthenticatedUser:
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

    if not allow_default_password_user:
        if not claims.get(HAS_SET_OWN_PASSWORD_FIELD, False):
            raise HTTPException(status_code=403, detail="User must change password")

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


def check_password_complexity(password: str) -> bool:
    """
    - password length is at least 8 characters
    - contains both uppercase and lowercase letters
    - contains at least one digit
    - contains at least one special character
    """
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    if not re.search(r"[@#$%^&+=!]", password):
        return False
    return True


def change_user_password(
    user: AuthenticatedUser, old_password: str, new_password: str
) -> None:
    # you should check the old password here
    # see eg: https://stackoverflow.com/a/71398321

    if not check_password_complexity(password=new_password):
        raise HTTPException(
            status_code=400, detail="Password must meet complexity requirements"
        )

    app = get_firebase_app()
    firebase_admin.auth.update_user(user.id, password=new_password, app=app)

    custom_claims = firebase_admin.auth.get_user(user.id, app).custom_claims
    custom_claims[HAS_SET_OWN_PASSWORD_FIELD] = True
    firebase_admin.auth.set_custom_user_claims(
        user.id, custom_claims=custom_claims, app=app
    )
