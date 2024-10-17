from pprint import pprint

import firebase_admin.auth
from typer import Option, Typer

from lta.api.configuration import Environment, get_firebase_app, set_environment
from lta.authentication import HAS_SET_OWN_PASSWORD_FIELD

app = Typer()


@app.command()
def set_admin(
    user_id: str = Option(...),
) -> None:
    set_environment(Environment.LOCAL_PROD)
    app = get_firebase_app()
    custom_claims = firebase_admin.auth.get_user(user_id, app).custom_claims
    if custom_claims is None:
        custom_claims = dict()
    custom_claims["admin"] = True
    firebase_admin.auth.set_custom_user_claims(
        user_id, custom_claims=custom_claims, app=app
    )


@app.command()
def set_has_set_own_password(
    user_id: str = Option(...),
) -> None:
    set_environment(Environment.LOCAL_PROD)
    app = get_firebase_app()
    custom_claims = firebase_admin.auth.get_user(user_id, app).custom_claims
    if custom_claims is None:
        custom_claims = dict()
    custom_claims[HAS_SET_OWN_PASSWORD_FIELD] = True
    firebase_admin.auth.set_custom_user_claims(
        user_id, custom_claims=custom_claims, app=app
    )


@app.command()
def get_claims(
    user_id: str = Option(...),
) -> None:
    set_environment(Environment.LOCAL_PROD)
    app = get_firebase_app()
    custom_claims = firebase_admin.auth.get_user(user_id, app).custom_claims
    pprint(custom_claims)


if __name__ == "__main__":
    app()
