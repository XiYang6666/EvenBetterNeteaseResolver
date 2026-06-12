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
    cookie_path = Path(get_config().cookie_path)
    if not cookie_path.exists():
        cookie_path.write_text(
            '{\n    "__remember_me": "true",\n    "os": "pc"\n}',
            encoding="utf-8",
        )

    ebnr = EBNR(semaphore=api_semaphore.value)
    ebnr.load_cookies_json(cookie_path)
    return ebnr
