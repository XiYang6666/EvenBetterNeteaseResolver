from asyncio import Semaphore

import httpx

from ebnr.config import get_config
from ebnr.services.async_resource import register_resource
from ebnr.utils.http import ssl_context
from ebnr.utils.lazy import Lazy

api_semaphore = Lazy(lambda: Semaphore(get_config().api_concurrency))
http_client = register_resource(httpx.AsyncClient(verify=ssl_context))
