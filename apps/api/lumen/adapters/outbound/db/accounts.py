"""Local account persistence and password handling."""

from uuid import UUID

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError
from sqlalchemy import delete, func, select, text
from sqlalchemy.exc import IntegrityError

from lumen.adapters.outbound.db.models import UserAccount, UserSession
from lumen.adapters.outbound.db.tickets import storage_session


class AccountConflict(Exception):
    pass


class AccountMissing(Exception):
    pass


def clean_username(username: str) -> str:
    value = username.strip()
    if not value or len(value) > 150 or "\x00" in value:
        raise ValueError("Username must contain between 1 and 150 characters.")
    return value


def validate_password(password: str) -> None:
    if len(password) < 12 or len(password) > 1024 or "\x00" in password:
        raise ValueError("Password must contain between 12 and 1024 characters.")


hasher = PasswordHasher()


def hash_password(password: str) -> str:
    validate_password(password)
    return hasher.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    try:
        return hasher.verify(password_hash, password)
    except (VerifyMismatchError, InvalidHashError):
        return False


class PostgresAccounts:
    def __init__(self, sessions):
        self.sessions = sessions

    async def list(self):
        async with storage_session(self.sessions) as session:
            return list((await session.scalars(select(UserAccount).order_by(UserAccount.username))).all())

    async def change_password(self, user_id: UUID, current: str, replacement: str):
        encoded = hash_password(replacement)
        async with storage_session(self.sessions) as session:
            user = await session.get(UserAccount, user_id, with_for_update=True)
            if user is None or not user.active or not verify_password(user.password_hash, current):
                raise AccountConflict("Current password is incorrect.")
            user.password_hash = encoded
            await session.execute(delete(UserSession).where(UserSession.user_id == user_id))
            await session.commit()

    async def create(self, username: str, password: str, role: str):
        username = clean_username(username)
        if role not in ("administrator", "operator"):
            raise ValueError("Invalid role.")
        password_hash = hash_password(password)
        async with storage_session(self.sessions) as session:
            try:
                user = UserAccount(username=username, password_hash=password_hash, role=role, active=True)
                session.add(user)
                await session.commit()
                return user
            except IntegrityError:
                raise AccountConflict("Username is already in use.") from None

    async def update(self, user_id: UUID, *, role: str | None = None, active: bool | None = None, password: str | None = None):
        if role is not None and role not in ("administrator", "operator"):
            raise ValueError("Invalid role.")
        password_hash = hash_password(password) if password is not None else None
        async with storage_session(self.sessions) as session:
            # One transaction-wide lock serializes all administrator changes, including bootstrap.
            await session.execute(text("SELECT pg_advisory_xact_lock(717380432)"))
            user = await session.get(UserAccount, user_id, with_for_update=True)
            if user is None:
                raise AccountMissing
            removing_admin = user.active and user.role == "administrator" and (active is False or (role is not None and role != "administrator"))
            if removing_admin:
                count = await session.scalar(select(func.count()).select_from(UserAccount).where(UserAccount.active.is_(True), UserAccount.role == "administrator"))
                if count <= 1:
                    raise AccountConflict("The last active administrator cannot be removed.")
            if role is not None:
                user.role = role
            if active is not None:
                user.active = active
            if password_hash is not None:
                user.password_hash = password_hash
            if active is False or password_hash is not None:
                await session.execute(delete(UserSession).where(UserSession.user_id == user.id))
            await session.commit()
            return user
