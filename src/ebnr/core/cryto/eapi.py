import hashlib
import json
import random

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

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
