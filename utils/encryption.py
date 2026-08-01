from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

KEY = b"1234567890123456"


def encrypt(data):
    cipher = AES.new(KEY, AES.MODE_ECB)
    return cipher.encrypt(pad(data, AES.block_size))


def decrypt(data):
    cipher = AES.new(KEY, AES.MODE_ECB)
    return unpad(cipher.decrypt(data), AES.block_size)