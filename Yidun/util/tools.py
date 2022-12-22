# -*- coding: utf-8 -*-
# @Project : Yidun
# @Time    : 2022/12/7 15:12
# @Author  : MuggleK
# @File    : tools.py

import random
from urllib.parse import unquote

import requests

import time
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import algorithms
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex

session = requests.session()


class AESCrypt:
    """
    AES 加解密
    """

    def __init__(self, key, iv):
        self.key = key.encode('utf-8')
        self.iv = iv.encode('utf-8')

    # 加密函数，如果text不足16位就用空格补足为16位，
    # 如果大于16当时不是16的倍数，那就补足为16的倍数。
    def encrypt(self, text):
        """
        加密
        :param text: 密文
        :return:
        """
        cryptor = AES.new(self.key, AES.MODE_CBC, self.iv)
        text = text.encode('utf-8')

        # 这里密钥key 长度必须为16（AES-128）,
        # 24（AES-192）,或者32 （AES-256）Bytes 长度
        # 目前AES-128 足够目前使用

        text = self.pkcs7_padding(text)

        ciphertext = cryptor.encrypt(text)

        # 因为AES加密时候得到的字符串不一定是ascii字符集的，输出到终端或者保存时候可能存在问题
        # 所以这里统一把加密后的字符串转化为16进制字符串
        return b2a_hex(ciphertext).decode()

    def decrypt(self, text):
        """
        解密
        :param text: 密文
        :return:
        """
        if not isinstance(text, bytes):
            text = text.encode()
        cryptor = AES.new(self.key, AES.MODE_CBC, self.iv)
        plain_text = cryptor.decrypt(a2b_hex(text))
        return bytes.decode(plain_text).rstrip()

    @staticmethod
    def pkcs7_padding(data):
        if not isinstance(data, bytes):
            data = data.encode()

        padder = padding.PKCS7(algorithms.AES.block_size).padder()

        padded_data = padder.update(data) + padder.finalize()

        return padded_data

    @staticmethod
    def pkcs7_unpadding(padded_data):
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        data = unpadder.update(padded_data)

        try:
            uppadded_data = data + unpadder.finalize()
        except ValueError:
            raise Exception('无效的加密信息! ')
        else:
            return uppadded_data


def format_print(api, text):
    """
    格式化输出, 增加时间
    :param api:
    :param text:
    :return:
    """
    text = '[{}] [{}] {}'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())), api, text)
    print('=' * 192)
    print(text)


def B():
    b_str = "xxxxxxxxxxxx4xxxyxxxxxxxxxxxxxxx"

    def bb(a):
        b = int(16 * random.random())
        return baseN(b if "x" == a else b & 3 | 8, 16)

    b_str = ''.join([bb(i) for i in b_str if i == "x" or i == "y"][2:9]) + "0"
    return b_str


def baseN(num, b):
    return ((num == 0) and "0") or (baseN(num // b, b).lstrip("0") + "0123456789abcdefghijklmnopqrstuvwxyz"[num % b])


def C():
    c_str = int(str(random.random())[2:])
    return baseN(c_str, 36)[:7]


def get_proxies():
    """
    @return:
    """
    proxy = session.get(f"http://192.168.9.3:55555/random").text.strip()
    return {'http': 'http://' + proxy, 'https': 'http://' + proxy}


def str_to_dict(string):
    data = dict()
    for s in string.split("&"):
        s_split = s.split("=")
        data[s_split[0]] = unquote(s_split[1])
    return data
