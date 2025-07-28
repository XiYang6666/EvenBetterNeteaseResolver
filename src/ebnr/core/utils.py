import base64
import hashlib
import json
import random
import re
import urllib.parse
from xmlrpc.client import boolean

import httpx
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from ebnr.core.cookie import get_cookies

AES_KEY = b"e82ckenh8dichen8"
ID_MAGIC = "3go8&$8*3*3h0k(2)2"


def make_eapi_params(path: str, payload: str):
    # 构造参数
    text = f"nobody{path}use{payload}md5forencrypt"
    digest = hashlib.md5(text.encode()).hexdigest()
    params = f"{path}-36cd479b6b5-{payload}-36cd479b6b5-{digest}"
    # 加密
    aes = algorithms.AES(AES_KEY)
    padder = padding.PKCS7(aes.block_size).padder()
    padded_data = padder.update(params.encode()) + padder.finalize()
    cipher = Cipher(aes, modes.ECB())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    encrypted_params = encrypted_data.hex()
    return encrypted_params


def make_eapi_header():
    data = {
        "os": "pc",
        "appver": "",
        "osver": "",
        "deviceId": "pyncm!",
        "requestId": str(random.randrange(20000000, 30000000)),
    }
    return json.dumps(data)


def make_encrypted_id(id: str):
    transformed_id = "".join(
        chr(ord(id[i]) ^ ord(ID_MAGIC[i % len(ID_MAGIC)])) for i in range(len(id))
    )
    hashed_id = hashlib.md5(transformed_id.encode()).digest()
    encoded_id = base64.b64encode(hashed_id).decode()
    replaced_id = encoded_id.replace("/", "_").replace("+", "-")
    return replaced_id


def make_client(with_cookie: boolean = True):
    return httpx.AsyncClient(
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36 Chrome/91.0.4472.164 NeteaseMusicDesktop/2.10.2.200154",
            "Referer": "",
        },
        cookies=get_cookies() if with_cookie else None,
    )


def fix_song_url(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    host = parsed.netloc
    assert host is not None, "Invalid URL"
    new_host = re.sub(
        r"^m([78])04\.music\.126\.net$",
        lambda m: f"m{m.group(1)}01.music.126.net",
        host,
    )
    result = parsed._replace(scheme="https", netloc=new_host).geturl()
    return result
