# src/utils/encrypt.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/30
# @Author  : Aaron Zhou
# @File    : encrypt.py
# @Software: Cursor
# @Description: 加密解密工具
import hashlib
import os
import secrets
import string

from typing import Any

from cryptography.hazmat.backends.openssl import backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from itsdangerous import URLSafeSerializer
from passlib.context import CryptContext

from src.common.logger import log


class AESCipher:
    """AES 加密解密类"""
    def __init__(self, key: bytes | str) -> None:
        """
        :param key: 密钥，16/24/32 bytes 或 16 进制字符串
        """
        self.key = key if isinstance(key, bytes) else bytes.fromhex(str(key))

    def encrypt(self, plaintext: bytes | str) -> bytes:
        """
        AES 加密

        :param plaintext: 加密前的明文
        :return:
        """
        if not isinstance(plaintext, bytes):
            plaintext = str(plaintext).encode('utf-8')
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=backend)
        encryptor = cipher.encryptor()
        padder = padding.PKCS7(cipher.algorithm.block_size).padder()  # type: ignore
        padded_plaintext = padder.update(plaintext) + padder.finalize()
        ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()
        return iv + ciphertext

    def decrypt(self, ciphertext: bytes | str) -> str:
        """
        AES 解密

        :param ciphertext: 解密前的密文, bytes 或 16 进制字符串
        :return:
        """
        ciphertext = ciphertext if isinstance(ciphertext, bytes) else bytes.fromhex(str(ciphertext))
        iv = ciphertext[:16]
        ciphertext = ciphertext[16:]
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=backend)
        decryptor = cipher.decryptor()
        unpadder = padding.PKCS7(cipher.algorithm.block_size).unpadder()  # type: ignore
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
        return plaintext.decode('utf-8')


class Md5Cipher:
    """MD5 加密类"""
    @staticmethod
    def encrypt(plaintext: bytes | str) -> str:
        """
        MD5 加密

        :param plaintext: 加密前的明文
        :return:
        """
        sha256 = hashlib.sha256()
        if not isinstance(plaintext, bytes):
            plaintext = str(plaintext).encode('utf-8')
        sha256.update(plaintext)
        return sha256.hexdigest()


class ItsDCipher:
    """ItsDangerous 加密解密类"""
    def __init__(self, key: bytes | str) -> None:
        """
        :param key: 密钥，16/24/32 bytes 或 16 进制字符串
        """
        self.key = key if isinstance(key, bytes) else bytes.fromhex(str(key))

    def encrypt(self, plaintext: Any) -> str:
        """
        ItsDangerous 加密 (可能失败，如果 plaintext 无法序列化，则会加密为 MD5)

        :param plaintext: 加密前的明文
        :return:
        """
        serializer = URLSafeSerializer(self.key)
        try:
            ciphertext = serializer.dumps(plaintext)
        except Exception as e:
            log.error(f'ItsDangerous encrypt failed: {e}')
            ciphertext = Md5Cipher.encrypt(plaintext)
        return str(ciphertext)

    def decrypt(self, ciphertext: str) -> Any:
        """
        ItsDangerous 解密 (可能失败，如果 ciphertext 无法反序列化，则解密失败, 返回原始密文)

        :param ciphertext: 解密前的密文
        :return:
        """
        serializer = URLSafeSerializer(self.key)
        try:
            plaintext = serializer.loads(ciphertext)
        except Exception as e:
            log.error(f'ItsDangerous decrypt failed: {e}')
            plaintext = ciphertext
        return plaintext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_salt(length: int = 16) -> str:
    """生成随机盐值"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def hash_password(password: str, salt: str) -> str:
    """
    使用bcrypt加密密码

    Args:
        password: 原始密码
        salt: 盐值
    """
    return pwd_context.hash(password + salt)


def verify_password(plain_password: str, salt: str, hashed_password: str) -> bool:
    """
    验证密码

    Args:
        plain_password: 原始密码
        salt: 盐值
        hashed_password: 加密后的密码
    """
    return pwd_context.verify(plain_password + salt, hashed_password)
