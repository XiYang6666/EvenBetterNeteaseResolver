from asyncio import Semaphore
from typing import Optional

from ebnr.config import get_config

api_semaphore: Optional[Semaphore] = None


def get_api_semaphore():
    global api_semaphore
    if not api_semaphore:
        api_semaphore = Semaphore(get_config().api_concurrency)
    return api_semaphore
