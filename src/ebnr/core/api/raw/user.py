from ebnr.core.cryto.weapi import make_weapi_form
from ebnr.core.utils import make_client


async def get_user_info() -> dict:
    request_url = "https://music.163.com/weapi/nuser/account/get"
    form = make_weapi_form("{}")
    async with make_client() as client:
        response = await client.post(request_url, data=form)
    return response.json()
