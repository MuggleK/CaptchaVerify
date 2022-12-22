import cv2
import json
import base64
import requests
from PIL import Image
import numpy as np
from loguru import logger

from settings import base_settings, isDebug


def img_recover(buffer):
    image = np.asarray(bytearray(buffer), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)

    img = Image.fromarray(image)
    serialize = [39, 38, 48, 49, 41, 40, 46, 47, 35, 34, 50, 51, 33, 32, 28, 29, 27, 26, 36, 37, 31, 30, 44, 45, 43,
                 42, 12, 13, 23, 22, 14, 15, 21, 20, 8, 9, 25, 24, 6, 7, 3, 2, 0, 1, 11, 10, 4, 5, 19, 18, 16, 17]
    target = Image.new('RGB', (260, 160))

    for i in range(52):
        u = serialize[i] % 26 * 12
        c = 80 if 25 < serialize[i] else 0
        box = (u, c, u + 10, c + 80)
        region = img.crop(box)
        b = 80 if 25 < i else 0
        target.paste(region, (i % 26 * 10, b))

    return target


def chinese_recognize(captcha):
    image = base64.b64encode(captcha).decode()
    res = requests.post(url=base_settings['Chinese']['url'], data=json.dumps({'img': image}))
    data = res.json().get('data')

    if isDebug:
        logger.debug(f'极验文字点选识别结果： {data}')

    return data


def nine_recognize(captcha):
    image = base64.b64encode(captcha).decode()
    res = requests.post(url=base_settings['Nine_Click']['url'], data=json.dumps({'img': image}))
    data = res.json().get('data')

    if isDebug:
        logger.debug(f'极验九宫格识别结果： {data}')

    return data


def space_recognize(captcha, sign):
    image = base64.b64encode(captcha).decode()
    res = requests.post(url=base_settings['Space_verify']['url'], data=json.dumps({'img': image, 'semantics': sign}))
    data = res.json().get('data')

    if isDebug:
        logger.debug(f'极验空间点选识别结果： {data}')

    if data:
        return data.get('position')

    return None


def icon_recognize(captcha):
    image = base64.b64encode(captcha).decode()
    res = requests.post(url=base_settings['Icon']['url'], data=json.dumps({'img': image}))
    data = res.json().get('data')

    if isDebug:
        logger.debug(f'极验图标点选识别结果： {data}')

    return data


class SlideCrack:
    def __init__(self, gap_img, bg):
        self.gap_img = gap_img
        self.bg = bg

    @staticmethod
    def pixel_is_equal(image1, image2, x, y):
        """
        判断两张图片的像素是否相等,不想等即为缺口位置
        :param image1:
        :param image2:
        :param x:  x坐标
        :param y: y 坐标
        :return:
        """
        # 取两个图片的像素点
        pixel1 = image1.load()[x, y]
        pixel2 = image2.load()[x, y]
        threshold = 60  # 像素色差
        if abs(pixel1[0] - pixel2[0]) < threshold and abs(pixel1[1] - pixel2[1]) < threshold and abs(
                pixel1[2] - pixel2[2]) < threshold:
            return True
        else:
            return False

    def get_gap(self):
        """
        获取缺口位置
        :return:
        """
        left = 50  # 设置一个起始量,因为验证码一般不可能在左边，加快识别速度
        for i in range(left, self.gap_img.size[0]):
            for j in range(self.gap_img.size[1]):
                if not self.pixel_is_equal(self.gap_img, self.bg, i, j):
                    left = i
                    return left
        return left
