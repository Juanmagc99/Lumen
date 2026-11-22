"""Opaque sessions and persistent sign-in throttling."""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, func, select, text

from lumen.adapters.outbound.db.accounts import hasher, verify_password
from lumen.adapters.outbound.db.models import SignInCounter, UserAccount, UserSession
from lumen.adapters.outbound.db.tickets import storage_session

SESSION_LIFETIME = timedelta(hours=12)
WINDOW = timedelta(minutes=15)
FAILURE_LIMIT = 5
COUNTER_LIMIT = 10000
_DUMMY_HASH = hasher.hash(secrets.token_urlsafe(32))


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class PostgresAuthentication:
    def __init__(self, sessions, failure_limit: int = FAILURE_LIMIT):
        if failure_limit < 1:
            raise ValueError("Sign-in failure limit must be positive.")
        self.sessions = sessions
        self.failure_limit = failure_limit

    async def sign_in(self, username: str, password: str, address: str):
        now = datetime.now(timezone.utc)
        keys = sorted({digest("user:" + username.strip().lower()), digest("address:" + address)})
        async with storage_session(self.sessions) as session:
            # Bound and serialize counter creation across API processes.
            await session.execute(text("SELECT pg_advisory_xact_lock(717380433)"))
            await session.execute(delete(SignInCounter).where(SignInCounter.window_started_at < now - WINDOW * 2, (SignInCounter.blocked_until.is_(None)) | (SignInCounter.blocked_until <= now)))
            existing = set((await session.scalars(select(SignInCounter.key).where(SignInCounter.key.in_(keys)))).all())
            count = await session.scalar(select(func.count()).select_from(SignInCounter))
            if count + len(set(keys) - existing) > COUNTER_LIMIT:
                await session.commit()
                return None
            counters = []
            for key in keys:
                counter = await session.get(SignInCounter, key)
                if counter is None:
                    counter = SignInCounter(key=key, failures=0, window_started_at=now)
                    session.add(counter)
                elif counter.window_started_at <= now - WINDOW and (counter.blocked_until is None or counter.blocked_until <= now):
                    counter.failures = 0
                    counter.window_started_at = now
                    counter.blocked_until = None
                counters.append(counter)
            account = await session.scalar(select(UserAccount).where(func.lower(UserAccount.username) == username.strip().lower()).with_for_update())
            valid = verify_password(account.password_hash if account else _DUMMY_HASH, password)
            blocked = any(counter.blocked_until is not None and counter.blocked_until > now for counter in counters)
            if blocked or account is None or not account.active or not valid:
                if not blocked:
                    for counter in counters:
                        counter.failures += 1
                        if counter.failures >= self.failure_limit:
                            counter.blocked_until = now + WINDOW
                await session.commit()
                return None
            for counter in counters:
                counter.failures = 0
                counter.window_started_at = now
                counter.blocked_until = None
            token = secrets.token_urlsafe(32)
            session.add(UserSession(token_digest=digest(token), user_id=account.id, expires_at=now + SESSION_LIFETIME))
            await session.commit()
            return token

    async def current(self, token: str):
        async with storage_session(self.sessions) as session:
            return await session.scalar(select(UserAccount).join(UserSession, UserSession.user_id == UserAccount.id).where(UserSession.token_digest == digest(token), UserSession.expires_at > datetime.now(timezone.utc), UserAccount.active.is_(True)))

    async def sign_out(self, token: str):
        async with storage_session(self.sessions) as session:
            await session.execute(delete(UserSession).where(UserSession.token_digest == digest(token)))
            await session.commit()
