import binascii
from typing import Any

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

LINUXAPI_KEY = b"rFgB&h#%2?^eDg:Q"


def aes_ecb_encrypt(data: bytes, key: bytes) -> bytes:
    cipher = Cipher(algorithms.AES(key), modes.ECB())
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data) + padder.finalize()
    return encryptor.update(padded_data) + encryptor.finalize()


def make_linuxapi_data(method: str, url: str, params: Any):
    return {"method": method, "url": url, "params": params}


def make_linuxapi_form(data: str):
    ciphertext = aes_ecb_encrypt(data.encode(), LINUXAPI_KEY)
    return {"eparams": binascii.hexlify(ciphertext).upper().decode()}
