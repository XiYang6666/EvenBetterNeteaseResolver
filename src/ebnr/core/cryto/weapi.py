import base64
import secrets
from typing import Tuple

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

_IV = b"0102030405060708"
_PRESET_KEY = b"0CoJUm6Qyw8W8jud"
_STD_CHARS = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
_PUBLIC_KEY_PEM = b"""-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDgtQn2JZ34ZC28NWYpAUd98iZ3
7BUrX/aKzmFbt7clFSs6sXqHauqKWqdtLkF2KexO40H1YTX8z2lSgBBOAxLsvaklV
8k4cBFK9snQXE9/DDaFt6Rr7iVZMldczhC0JNgTz+SHXT6CBHuX3e9SdB1Ua44onc
aTWz7OBGLbCiK45wIDAQAB
-----END PUBLIC KEY-----"""

_PUBLIC_KEY = serialization.load_pem_public_key(
    _PUBLIC_KEY_PEM, backend=default_backend()
)


def pkcs7_pad(data: bytes, block_size: int = 16) -> bytes:
    pad_len = block_size - (len(data) % block_size)
    return data + bytes([pad_len]) * pad_len


def aes_cbc_encrypt(data: bytes, key: bytes, iv: bytes) -> bytes:
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padded = pkcs7_pad(data, 16)
    return encryptor.update(padded) + encryptor.finalize()


def new_len16_rand() -> Tuple[bytes, bytes]:
    rand_bytes = bytes(secrets.choice(_STD_CHARS) for _ in range(16))
    rand_bytes_rev = rand_bytes[::-1]
    return rand_bytes, rand_bytes_rev


def rsa_encrypt_no_padding(secret_key: bytes) -> bytes:
    assert isinstance(_PUBLIC_KEY, rsa.RSAPublicKey)
    numbers = _PUBLIC_KEY.public_numbers()
    n = numbers.n
    e = numbers.e

    # 固定128字节长度，前面补0填充
    padded_key = b"\x00" * (128 - len(secret_key)) + secret_key
    m = int.from_bytes(padded_key, "big")
    c = pow(m, e, n)

    # 确保长度为128字节，不足左侧补0
    encrypted = c.to_bytes(128, "big")
    return encrypted


def make_weapi_form(data: str) -> dict:
    # 生成随机密钥及其反转
    secret_key, reversed_key = new_len16_rand()

    # 第一次 AES-CBC（preset_key）
    first_encrypted = aes_cbc_encrypt(data.encode("utf-8"), _PRESET_KEY, _IV)
    first_b64 = base64.b64encode(first_encrypted)

    # 第二次 AES-CBC（reversed_key）
    second_encrypted = aes_cbc_encrypt(first_b64, reversed_key, _IV)
    params = base64.b64encode(second_encrypted).decode("utf-8")

    # RSA 无 padding 加密 secret_key
    enc_sec_key = rsa_encrypt_no_padding(secret_key).hex()

    return {"params": params, "encSecKey": enc_sec_key}
