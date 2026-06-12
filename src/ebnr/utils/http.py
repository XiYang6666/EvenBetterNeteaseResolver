import ssl

import httpx

ssl_context = ssl.create_default_context()

async def streaming_request(method: str, url: str, chunk_size: int = 1024):
    async_client = httpx.AsyncClient()
    response = await async_client.send(httpx.Request(method, url), stream=True)

    async def data_generator():
        async for chunk in response.aiter_bytes(chunk_size=chunk_size):
            yield chunk
        await response.aclose()
        await async_client.aclose()

    return response, data_generator()
