import pytest

from ebnr.core.api.raw.user import get_user_info


@pytest.mark.asyncio
async def test_user_info():
    await get_user_info()
