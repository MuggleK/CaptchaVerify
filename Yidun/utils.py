# -*- coding: utf-8 -*-
import time
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import algorithms
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex


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


if __name__ == '__main__':
    # format_print('CaptchaCracker', 'Hello, World! ')
    x = AESCrypt('jo8j9wGw%6HbxfFn', '0123456789ABCDEF').decrypt(
        "95780ba0943730051dccb5fe3918f9feac71754fea3873b762f5f4526de59281c409d31d10e3188ac1c6904df1ee1785f540add027020caecfdb52c66f416181"
    )
    print(x)
