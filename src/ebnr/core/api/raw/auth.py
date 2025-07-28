import json

from httpx import Response

from ebnr.core.utils import make_client, make_eapi_header, make_eapi_params


async def create_qrcode_unikey() -> dict:
    request_url = "https://interface3.music.163.com/eapi/login/qrcode/unikey"
    eapi_path = "/api/login/qrcode/unikey"
    payload = {"type": 1, "header": make_eapi_header()}
    params = make_eapi_params(eapi_path, json.dumps(payload))
    async with make_client(False) as client:
        response = await client.post(request_url, params={"params": params})
    return response.json()


async def check_qrcode_satsus(unikey: str) -> Response:
    request_url = "https://interface3.music.163.com/eapi/login/qrcode/client/login"
    eapi_path = "/api/login/qrcode/client/login"
    payload = {"key": unikey, "type": 1, "header": make_eapi_header()}
    params = make_eapi_params(eapi_path, json.dumps(payload))
    async with make_client(False) as client:
        return await client.post(request_url, params={"params": params})
