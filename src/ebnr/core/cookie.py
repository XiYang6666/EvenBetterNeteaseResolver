import json
from pathlib import Path

netease_cookie: dict[str, str] = {}


def set_cookies(cookie: dict[str, str]) -> None:
    global netease_cookie
    netease_cookie = cookie


def get_cookies() -> dict[str, str]:
    assert netease_cookie is not None, "Cookies not set yet."
    return netease_cookie


def load_cookies(path: Path):
    global netease_cookie
    if not path.exists():
        netease_cookie = {}
        return
    with open(path, "r", encoding="utf-8") as f:
        netease_cookie = json.load(f)


def save_cookies(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(get_cookies(), f)
