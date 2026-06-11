import pytest


@pytest.fixture(scope="session", autouse=True)
def init_config():
    from ebnr.config import load_config

    load_config()
