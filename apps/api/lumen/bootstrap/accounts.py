"""Interactive local account bootstrap and recovery."""

import argparse
import asyncio
import getpass
import os

from sqlalchemy import func, select, text

from lumen.adapters.outbound.db.accounts import PostgresAccounts, clean_username, hash_password, hasher, validate_password
from lumen.adapters.outbound.db.models import UserAccount
from lumen.adapters.outbound.db.session import DatabaseSessions
from lumen.bootstrap.config import database_url


async def bootstrap(sessions, username: str, password: str):
    username = clean_username(username)
    encoded = hash_password(password)
    async with sessions.scope() as session:
        await session.execute(text("SELECT pg_advisory_xact_lock(717380432)"))
        if await session.scalar(select(func.count()).select_from(UserAccount)):
            raise ValueError("Bootstrap is only available when no accounts exist.")
        session.add(UserAccount(username=username, password_hash=encoded, role="administrator", active=True))
        await session.commit()


async def recover(sessions, username: str, password: str):
    username = clean_username(username)
    async with sessions.scope() as session:
        user_id = await session.scalar(select(UserAccount.id).where(func.lower(UserAccount.username) == username.lower(), UserAccount.role == "administrator"))
    if user_id is None:
        raise ValueError("Administrator account not found.")
    await PostgresAccounts(sessions).update(user_id, password=password)


async def bootstrap_from_environment(sessions):
    username = os.environ.get("LUMEN_ADMIN_USERNAME", "")
    password = os.environ.get("LUMEN_ADMIN_PASSWORD", "")
    if not username and not password:
        return False
    if not username or not password.strip() or len(password) > 1024 or "\x00" in password:
        raise ValueError("Set both local administrator settings to nonblank values.")
    username = clean_username(username)
    async with sessions.scope() as session:
        await session.execute(text("SELECT pg_advisory_xact_lock(717380432)"))
        if await session.scalar(select(func.count()).select_from(UserAccount)):
            return False
        session.add(UserAccount(username=username, password_hash=hasher.hash(password), role="administrator", active=True))
        await session.commit()
        return True


def main():
    parser = argparse.ArgumentParser(description="Manage local administrator access interactively.")
    parser.add_argument("action", choices=("bootstrap", "bootstrap-env", "recover"))
    args = parser.parse_args()
    if args.action == "bootstrap-env":
        try:
            created = asyncio.run(bootstrap_from_environment(DatabaseSessions(database_url)))
        except ValueError as exc:
            parser.error(str(exc))
        print("Initial administrator created." if created else "Initial administrator unchanged.")
        return
    username = getpass.getpass("Administrator username: ")
    password = getpass.getpass("New password: ")
    if password != getpass.getpass("Confirm password: "):
        parser.error("Passwords do not match.")
    try:
        validate_password(password)
        sessions = DatabaseSessions(database_url)
        asyncio.run(bootstrap(sessions, username, password) if args.action == "bootstrap" else recover(sessions, username, password))
    except ValueError as exc:
        parser.error(str(exc))
    print("Administrator credentials updated.")


if __name__ == "__main__":
    main()
