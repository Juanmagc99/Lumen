"""Account and session API."""

from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field

from lumen.adapters.outbound.db.accounts import AccountConflict, AccountMissing

COOKIE_NAME = "lumen_session"


class Credentials(BaseModel):
    username: str = Field(min_length=1, max_length=150)
    password: str = Field(min_length=1, max_length=1024)


class AccountCreate(Credentials):
    role: Literal["administrator", "operator"]


class AccountUpdate(BaseModel):
    role: Literal["administrator", "operator"] | None = None
    active: bool | None = None
    password: str | None = Field(default=None, min_length=12, max_length=1024)


class PasswordChange(BaseModel):
    current_password: str = Field(min_length=1, max_length=1024)
    new_password: str = Field(min_length=12, max_length=1024)


def public_account(user):
    return {"id": str(user.id), "username": user.username, "role": user.role, "active": user.active}


def router_for_authentication(auth, accounts, secure_cookie: bool):
    router = APIRouter(prefix="/api/auth")

    async def current(request: Request):
        token = request.cookies.get(COOKIE_NAME)
        user = await auth.current(token) if token else None
        if user is None:
            raise HTTPException(401, "Sign in required.")
        return user

    async def administrator(user=Depends(current)):
        if user.role != "administrator":
            raise HTTPException(403, "Administrator access required.")
        return user

    @router.post("/login")
    async def login(data: Credentials, request: Request, response: Response):
        token = await auth.sign_in(data.username, data.password, request.client.host if request.client else "unknown")
        if token is None:
            raise HTTPException(401, "Sign-in failed.")
        response.set_cookie(COOKIE_NAME, token, max_age=43200, httponly=True, secure=secure_cookie, samesite="strict", path="/")
        return {"status": "signed_in"}

    @router.get("/session")
    async def get_session(user=Depends(current)):
        return public_account(user)

    @router.post("/logout")
    async def logout(request: Request, response: Response, user=Depends(current)):
        await auth.sign_out(request.cookies[COOKIE_NAME])
        response.delete_cookie(COOKIE_NAME, path="/", secure=secure_cookie, httponly=True, samesite="strict")
        return {"status": "signed_out"}

    @router.post("/password")
    async def change_password(data: PasswordChange, user=Depends(current)):
        try:
            await accounts.change_password(user.id, data.current_password, data.new_password)
        except (AccountConflict, ValueError) as exc:
            raise HTTPException(400, str(exc)) from None
        return {"status": "password_changed"}

    @router.get("/users")
    async def users(user=Depends(administrator)):
        return [public_account(account) for account in await accounts.list()]

    @router.post("/users", status_code=201)
    async def create_user(data: AccountCreate, user=Depends(administrator)):
        try:
            return public_account(await accounts.create(data.username, data.password, data.role))
        except AccountConflict as exc:
            raise HTTPException(409, str(exc)) from None
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from None

    @router.patch("/users/{user_id}")
    async def update_user(user_id: UUID, data: AccountUpdate, user=Depends(administrator)):
        try:
            return public_account(await accounts.update(user_id, **data.model_dump(exclude_unset=True)))
        except AccountMissing:
            raise HTTPException(404, "Account not found.") from None
        except AccountConflict as exc:
            raise HTTPException(409, str(exc)) from None
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from None

    return router
