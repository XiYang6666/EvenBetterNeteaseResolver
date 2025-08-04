import json
from pathlib import Path

COOKIE_FILE_PATH = Path("data/cookie.json")
netease_cookie: dict[str, str] = {}


def set_cookies(cookie: dict[str, str]) -> None:
    global netease_cookie
    netease_cookie = cookie
    save_cookies(cookie)


def get_cookies() -> dict[str, str]:
    assert netease_cookie is not None, "Cookies not set yet."
    return netease_cookie


def load_cookies():
    global netease_cookie
    if not COOKIE_FILE_PATH.exists():
        save_cookies({})
    with open(COOKIE_FILE_PATH, "r", encoding="utf-8") as f:
        netease_cookie = json.load(f)


def save_cookies(cookie: dict[str, str]) -> None:
    COOKIE_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(COOKIE_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(cookie, f)
