from ebnr.core.utils import make_client, make_eapi_params


async def get_user_info() -> dict:
    request_url = "https://music.163.com/eapi/v1/user/info"
    eapi_path = "/api/v1/user/info"
    params = make_eapi_params(eapi_path, "")
    async with make_client() as client:
        response = await client.post(request_url, data={"params": params})
    return response.json()
