from asyncio import Semaphore
from pathlib import Path

import httpx

from ebnr.config import get_config
from ebnr.core.client import EBNR
from ebnr.services.async_resource import register_resource
from ebnr.utils.http import ssl_context
from ebnr.utils.lazy import Lazy

api_semaphore = Lazy(lambda: Semaphore(get_config().api_concurrency))
http_client = register_resource(httpx.AsyncClient(verify=ssl_context))


@Lazy
def ebnr_client():
    cookie_file_path = Path(get_config().cookie_file_path)
    cookie_file_type = get_config().cookie_file_type
    config_cookie = get_config().cookie

    ebnr = EBNR(semaphore=api_semaphore.value)
    if config_cookie:
        pass
    elif not cookie_file_path.exists() and cookie_file_type == "object":
        cookie_file_path.parent.mkdir(parents=True, exist_ok=True)
        cookie_file_path.write_text("{}", encoding="utf-8")
    elif not cookie_file_path.exists() and cookie_file_type == "list":
        cookie_file_path.parent.mkdir(parents=True, exist_ok=True)
        cookie_file_path.write_text("[]", encoding="utf-8")

    if config_cookie:
        ebnr.set_cookies(config_cookie)
    elif cookie_file_type == "object":
        ebnr.load_cookies_json(cookie_file_path)
    elif cookie_file_type == "list":
        ebnr.load_cookies_json_list(cookie_file_path)

    return ebnr
