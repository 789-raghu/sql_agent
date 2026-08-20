from typing import Set

SENSITIVE_COLUMNS: Set[str] = {
    "password",
    "passwd",
    "api_key",
    "apikey",
    "token",
    "auth_token",
    "secret",
    "secret_key",
    "credentials",
    "private_key",
    "hash",
    "salt"
}
