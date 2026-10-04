"""Persist locally created Bao user accounts."""

from __future__ import annotations

import hashlib
import hmac
import json
import secrets
from pathlib import Path
from typing import cast

ACCOUNT_FILE = Path("data/users/accounts.json")


def account_file() -> Path:
    """Return the local account database path."""
    return ACCOUNT_FILE


def load_accounts(path: Path = ACCOUNT_FILE) -> dict[str, dict[str, str]]:
    """Load locally created accounts, returning an empty store when absent."""
    if not path.exists():
        return {}
    return cast(
        dict[str, dict[str, str]],
        json.loads(path.read_text(encoding="utf-8")),
    )


def hash_password(password: str, salt: str) -> str:
    """Return a scrypt password hash for a hexadecimal salt."""
    derived_key = hashlib.scrypt(
        password.encode("utf-8"),
        salt=bytes.fromhex(salt),
        n=2**14,
        r=8,
        p=1,
    )
    return derived_key.hex()


def create_account(
    username: str, password: str, path: Path = ACCOUNT_FILE
) -> dict[str, str]:
    """Create and persist one locally registered account."""
    accounts = load_accounts(path)
    if username in accounts:
        raise ValueError("Username is already in use.")

    salt = secrets.token_hex(16)
    account = {"salt": salt, "password_hash": hash_password(password, salt)}
    accounts[username] = account
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(accounts, indent=2), encoding="utf-8")
    return account


def authenticate_account(username: str, password: str) -> bool:
    """Return whether a locally registered account matches the credentials."""
    account = load_accounts().get(username)
    if account is None:
        return False
    expected_hash = hash_password(password, account["salt"])
    return hmac.compare_digest(expected_hash, account["password_hash"])
