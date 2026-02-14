"""Create admin user. Run from project root: python scripts/create_admin.py --username admin."""

import argparse
import asyncio
import os
import sys
from pathlib import Path

# Add project root so we can import users app
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", required=True, help="Admin username")
    args = parser.parse_args()
    # Load env from .env if present
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    # Defer async run
    asyncio.run(_create_admin(args.username))


async def _create_admin(username: str) -> None:
    import bcrypt

    from users.application.use_cases.create_user import CreateUserUseCase
    from users.config.settings import Settings
    from users.infrastructure.db.repositories.user_repository import UserRepositoryImpl
    from users.infrastructure.db.session import get_session_factory

    settings = Settings()
    session_factory = get_session_factory(settings)
    user_repo = UserRepositoryImpl(session_factory)
    use_case = CreateUserUseCase(user_repo, session_factory)
    raw = b"admin"[:72]
    password_hash = bcrypt.hashpw(raw, bcrypt.gensalt()).decode("utf-8")
    try:
        user = await use_case.run(username=username, password_hash=password_hash, is_admin=True)
        print(f"Admin user created: id={user.id}, username={user.username}")
    except Exception as e:
        if "already exists" in str(e).lower() or "unique" in str(e).lower():
            print(f"User '{username}' already exists.")
        else:
            raise
