import json
import random
import tempfile
from pathlib import Path
from uuid import uuid4

import pytest

from ebnr.core.cookie import get_cookies, load_cookies, save_cookies, set_cookies
from tests.utils import random_str


@pytest.mark.parametrize(
    "cookie",
    [
        {random_str(): random_str() for __ in range(random.randint(5, 10))}
        for _ in range(5)
    ],
)
def test_cookie_get_set(cookie: dict[str, str]):
    set_cookies(cookie)
    assert get_cookies() == cookie


@pytest.mark.parametrize(
    "cookie",
    [
        {random_str(): random_str() for __ in range(random.randint(5, 10))}
        for _ in range(5)
    ],
)
def test_cookie_save_load(cookie: dict[str, str]):
    path = Path(tempfile.gettempdir()) / f"cookie-{uuid4()}.json"
    set_cookies(cookie)
    save_cookies(path)
    assert json.loads(path.read_text("utf-8")) == cookie
    load_cookies(path)
    assert get_cookies() == cookie
