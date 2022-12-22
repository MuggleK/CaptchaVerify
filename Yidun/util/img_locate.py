# -*- coding: utf-8 -*-
import os
from io import BytesIO

import cv2
import requests
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import numpy as np
import uuid


class GapLocater:
    """
    滑块图片模板匹配
    """

    def __init__(self, gap, bg):
        """
        init code
        :param gap: 缺口图片
        :param bg: 背景图片
        :param out: 输出图片
        """
        self.gap = gap
        self.bg = bg
        # self.out = out

    @staticmethod
    def clear_white(img):
        """
        清除图片的空白区域，这里主要清除滑块的空白
        :param img:
        :return:
        """
        image = np.asarray(bytearray(img), dtype="uint8")
        img = cv2.imdecode(image, cv2.IMREAD_COLOR)
        # img = cv2.imread(img)
        rows, cols, channel = img.shape
        min_x = 255
        min_y = 255
        max_x = 0
        max_y = 0
        for x in range(1, rows):
            for y in range(1, cols):
                t = set(img[x, y])
                if len(t) >= 2:
                    if x <= min_x:
                        min_x = x
                    elif x >= max_x:
                        max_x = x

                    if y <= min_y:
                        min_y = y
                    elif y >= max_y:
                        max_y = y
        img1 = img[min_x: max_x, min_y: max_y]
        return img1

    def template_match(self, tpl, target):
        """
        背景匹配
        :param tpl:
        :param target:
        :return:
        """
        th, tw = tpl.shape[:2]
        result = cv2.matchTemplate(target, tpl, cv2.TM_CCOEFF_NORMED)
        # 寻找矩阵(一维数组当作向量,用Mat定义) 中最小值和最大值的位置
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        tl = max_loc
        br = (tl[0] + tw, tl[1] + th)
        # 绘制矩形边框，将匹配区域标注出来
        # target：目标图像
        # tl：矩形定点
        # br：矩形的宽高
        # (0, 0, 255)：矩形边框颜色
        # 1：矩形边框大小
        cv2.rectangle(target, tl, br, (0, 0, 255), 2)
        # cv2.imwrite(self.out, target)
        return tl

    @staticmethod
    def image_edge_detection(img):
        """
        图像边缘检测
        :param img:
        :return:
        """
        edges = cv2.Canny(img, 100, 200)
        return edges

    def run(self, is_clear_white=False):
        if is_clear_white:
            img1 = self.clear_white(self.gap)
        else:
            image = np.asarray(bytearray(self.gap), dtype="uint8")
            img1 = cv2.imdecode(image, cv2.IMREAD_COLOR)
            # img1 = cv2.imread(self.gap)
        img1 = cv2.cvtColor(img1, cv2.COLOR_RGB2GRAY)
        slide = self.image_edge_detection(img1)

        # back = cv2.imread(self.bg, 0)
        image = np.asarray(bytearray(self.bg), dtype="uint8")
        back = cv2.imdecode(image, cv2.IMREAD_COLOR)
        back = self.image_edge_detection(back)

        slide_pic = cv2.cvtColor(slide, cv2.COLOR_GRAY2RGB)
        back_pic = cv2.cvtColor(back, cv2.COLOR_GRAY2RGB)
        x = self.template_match(slide_pic, back_pic)
        # 输出横坐标, 即 滑块在图片上的位置
        return x


def _pic_download(url, ip):
    """
    图片下载
    :param url:
    :param ip:
    :return:
    """
    img_data = requests.get(url, proxies=ip).content
    content = img_data
    return content


def _get_distance(slider_url, captcha_url, ip):
    """
    获取缺口距离
    :param slider_url: 滑块图片 url
    :param captcha_url: 验证码图片 url
    :return:
    """
    # save_path = os.path.dirname(__file__).replace('\\', '/') + '/images'
    # if not os.path.exists(save_path):
    #     os.mkdir(save_path)

    # 引用上面的图片下载
    slider_content = _pic_download(slider_url, ip)

    # 引用上面的图片下载
    captcha_content = _pic_download(captcha_url, ip)
    img_size = Image.open(BytesIO(captcha_content)).size

    distance = GapLocater(slider_content, captcha_content).run(True)[0] + 3
    # os.remove(slider_path)
    # os.remove(captcha_path)
    return distance, img_size[0]


def make_word(text, width):
    """
    制作描述图片
    :return:
    """
    save_path = os.path.dirname(__file__).replace('\\', '/') + '/images'
    if not os.path.exists(save_path):
        os.mkdir(save_path)

    # 初始化图片对象, (320, 30)为图片大小, (255, 255, 255) 为白色背景
    img = Image.new('RGB', (width, 30), (255, 255, 255))
    # 设置字体
    font = ImageFont.truetype('/usr/share/fonts/simsun.ttc', 25)
    # 初始化写入对象
    draw = ImageDraw.Draw(img)
    # 添加文字, (0, 0): 文字起始坐标, (0, 0, 0): 颜色(黑色), font: 字体
    draw.text((25, 0), text, (0, 0, 0), font=font)
    # img.show()
    img_path = save_path + '/word.jpg'
    img.save(img_path)
    return img_path


def merge_word(img1, text, width):
    """
    将描述性文字合并到验证码图片上, 以便交给打码平台识别
    :return:
    """
    save_path = os.path.dirname(__file__).replace('\\', '/') + '/images'
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    new_image = Image.new('RGB', (width, width // 2 + 30))
    img1 = Image.open(img1).resize((width, width // 2))
    new_image.paste(img1, (0, 0))

    img2 = make_word(text, width)
    img2 = Image.open(img2)
    new_image.paste(img2, (0, width // 2))

    # new_image.show()
    img_path = save_path + '/new_captcha.jpg'
    new_image.save(img_path)
    return img_path


def judge_pos(xy):
    """
    根据图片左上角 (x, y) 判断是第几张图片
    :param xy:
    :return:
    """
    x = xy[0]
    y = xy[1]

    if 0 <= x < 40 and 0 <= y < 40:
        return 0
    elif 50 < x < 110 and 0 <= y < 40:
        return 1
    elif 130 < x < 190 and 0 <= y < 40:
        return 2
    elif 210 < x < 270 and 0 <= y < 40:
        return 3
    elif 0 <= x < 40 and 30 < y < 90:
        return 4
    elif 30 < x < 90 and 30 < y < 90:
        return 5
    elif 130 < x < 190 and 50 < y < 110:
        return 6
    else:
        return 7


def get_reverse_tuple(origin_dict):
    """
    例如 {0: 7, 1: 2, 2: 3, 3: 4, 4: 7, 7: 4, 8: 9, 9: 8, 10: 11}, 寻找顺序相反的位置元组
    :param origin_dict:
    :return:
    """
    for key, value in origin_dict.items():
        x = origin_dict.get(value, None)
        if x is not None and x == key:
            return ','.join(map(str, sorted([key, value])))
    return ''


def get_pos(captcha_path):
    """
    获取乱序图片还原交换位置
    :param captcha_path:
    :return:
    """
    save_path = os.path.dirname(__file__).replace('\\', '/') + '/images'
    if not os.path.exists(save_path):
        os.mkdir(save_path)

    captcha = Image.open(captcha_path)

    test_crop = captcha.crop((0, 0, 80, 80))
    test_path = save_path + '/ex_test.jpg'
    test_crop.save(test_path)

    origin_path = ''
    for k in range(4):
        path = save_path + f'/origin_{k}.jpg'
        try:
            xy = GapLocater(test_path, path, save_path + '/test_result.jpg').run()
        except:
            xy = None
        if xy:
            z = sum(xy)
            if 0 < z < 20 or 70 < z < 90 or 150 < z < 170 or 230 < z < 250 or 310 < z < 330:
                origin_path = path
                break

    result = {}
    # 将图片切割成 8 份, 与正确背景图片对比
    for i in range(4):
        crop = captcha.crop((80 * i, 0, 80 * i + 80, 80))
        upper_path = save_path + f'/upper_{i}.jpg'
        crop.save(upper_path)
        try:
            position = GapLocater(upper_path, origin_path, save_path + f'/exchange_upper_res_{i}.jpg').run()
        except:
            position = None
        if position and i != judge_pos(position):
            result[i] = judge_pos(position)

    for j in range(4):
        crop = captcha.crop((80 * j, 80, 80 * j + 80, 160))
        lower_path = save_path + f'/lower_{j}.jpg'
        crop.save(lower_path)
        try:
            position = GapLocater(lower_path, origin_path, save_path + f'/exchange_lower_res_{j}.jpg').run()
        except:
            position = None
        if position and j + 4 != judge_pos(position):
            result[j + 4] = judge_pos(position)

    final_pos = get_reverse_tuple(result)
    return final_pos


def read_pix(img):
    """
    读取像素
    :param img:
    :return:
    """
    x_0 = []
    x_80 = []
    y_0 = []
    y_80 = []
    for i in range(80):
        pix_0 = img.load()[0, i]
        x_0.append(pix_0[0])
        pix_80 = img.load()[79, i]
        x_80.append(pix_80[0])
    for j in range(80):
        pix_0 = img.load()[j, 0]
        y_0.append(pix_0[0])
        pix_80 = img.load()[j, 79]
        y_80.append(pix_80[0])
    return x_0, x_80, y_0, y_80


def is_merge_true(pix_list1, pix_list2):
    """
    判断两张图片是否正确拼接
    :param pix_list1:
    :param pix_list2:
    :return:
    """
    for i in range(len(pix_list1)):
        if abs(pix_list1[i] - pix_list2[i]) > 120:
            return False
    return True


def get_pos1(captcha_path):
    """
    获取乱序图片还原交换位置
    :param captcha_path:
    :return:
    """
    save_path = os.path.dirname(__file__).replace('\\', '/') + '/images'
    if not os.path.exists(save_path):
        os.mkdir(save_path)

    captcha = Image.open(captcha_path)
    # 将图片切割成 8 份
    for i in range(4):
        crop = captcha.crop((80 * i, 0, 80 * i + 80, 80))
        upper_path = save_path + f'/upper_{i}.jpg'
        crop.save(upper_path)
    for j in range(4):
        crop = captcha.crop((80 * j, 80, 80 * j + 80, 160))
        lower_path = save_path + f'/lower_{j}.jpg'
        crop.save(lower_path)

    u0 = Image.open(save_path + '/upper_0.jpg')
    u0_x0, u0_x80, u0_y0, u0_y80 = read_pix(u0)

    u1 = Image.open(save_path + '/upper_1.jpg')
    u1_x0, u1_x80, u1_y0, u1_y80 = read_pix(u1)

    u2 = Image.open(save_path + '/upper_2.jpg')
    u2_x0, u2_x80, u2_y0, u2_y80 = read_pix(u2)

    u3 = Image.open(save_path + '/upper_3.jpg')
    u3_x0, u3_x80, u3_y0, u3_y80 = read_pix(u3)

    l0 = Image.open(save_path + '/lower_0.jpg')
    l0_x0, l0_x80, l0_y0, l0_y80 = read_pix(l0)

    l1 = Image.open(save_path + '/lower_1.jpg')
    l1_x0, l1_x80, l1_y0, l1_y80 = read_pix(l1)

    l2 = Image.open(save_path + '/lower_2.jpg')
    l2_x0, l2_x80, l2_y0, l2_y80 = read_pix(l2)

    l3 = Image.open(save_path + '/lower_3.jpg')
    l3_x0, l3_x80, l3_y0, l3_y80 = read_pix(l3)

    if is_merge_true(u0_x80, u1_x0):
        if is_merge_true(u2_x80, u3_x0):
            if is_merge_true(l0_x80, l1_x0):
                return '6,7'
            elif is_merge_true(l2_x80, l3_x0):
                return '4,5'
            else:
                if is_merge_true(l1_x80, l2_x0):
                    return '4,7'
                else:
                    if is_merge_true(l0_x0, l1_x80) and is_merge_true(l0_x80, l3_x0):
                        return '4,6'
                    elif is_merge_true(l1_x0, l2_x80) and is_merge_true(l1_x80, l3_x0):
                        return '5,6'
                    elif is_merge_true(l1_x0, l2_x80) and is_merge_true(l1_y0, u3_x80):
                        return '5,7'
                    return None
        elif is_merge_true(u1_x0, u2_x80) and is_merge_true(u1_x80, u3_x0) and is_merge_true(u2_x0,
                                                                                             u0_x80) and is_merge_true(
                u1_y80, l1_y0) and is_merge_true(u2_y80, l2_y0):
            return '2,3'
        else:
            if is_merge_true(u3_y80, l3_y0):
                if is_merge_true(u2_y0, u0_y80) and is_merge_true(u2_x80, l1_x0):
                    return '2,4'
                elif is_merge_true(u2_x0, l0_x80) and is_merge_true(u2_y0, u1_y80) and is_merge_true(u2_x80, l2_x0):
                    return '2,5'
                elif is_merge_true(u2_x0, l1_x80) and is_merge_true(u2_y0, l2_y80) and is_merge_true(u2_x80, l3_x0):
                    return '2,6'
                elif is_merge_true(u2_x0, l2_x80) or is_merge_true(u2_y0, u3_y80):
                    return '2,7'
                return None
            else:
                if is_merge_true(u2_x0, l2_x80) and is_merge_true(u2_y0, u3_y80):
                    return '2,7'
                elif is_merge_true(u3_y0, u0_y80) and is_merge_true(u3_x80, l1_x0):
                    return '3,4'
                elif is_merge_true(u3_x0, l0_x80) and is_merge_true(u3_x80, l2_x0) and is_merge_true(u3_y0, u1_y80):
                    return '3,5'
                elif is_merge_true(u3_x0, l1_x80) or is_merge_true(u3_x80, l3_x0) or is_merge_true(u3_y0, u2_y80):
                    return '3,6'
                elif is_merge_true(u3_x0, l2_x80) or is_merge_true(u3_y0, l3_y80):
                    return '3,7'
                return None
    elif is_merge_true(u0_x0, u1_x80) and is_merge_true(u0_x80, u2_x0) and is_merge_true(u1_y80,
                                                                                         l0_y0) and is_merge_true(
            u0_y80, l1_y0):
        return '0,1'
    else:
        if is_merge_true(u1_x80, u2_x0):
            if is_merge_true(u0_x0, u1_x80) and is_merge_true(u0_x80, u3_x0) and is_merge_true(u0_y80, l2_y0):
                return '0,2'
            elif is_merge_true(u0_x0, u2_x80) and is_merge_true(u0_y80, l3_y0):
                return '0,3'
            elif is_merge_true(u0_y0, l0_y80) and is_merge_true(u0_x80, l1_x0):
                return '0,4'
            elif is_merge_true(u0_x0, l0_x80) and is_merge_true(u0_y0, u1_y80):
                return '0,5'
            elif is_merge_true(u0_x0, l1_x80) and is_merge_true(u0_y0, u2_y80):
                return '0,6'
            elif is_merge_true(u0_x0, l2_x80) or is_merge_true(u0_y0, u3_y80):
                return '0,7'
            return None
        else:
            if is_merge_true(u1_x0, u2_x80) and is_merge_true(u1_x80, u3_x0) and is_merge_true(u1_y80,
                                                                                               l2_y0) and is_merge_true(
                    u2_y80, l1_y0):
                return '1,2'
            elif is_merge_true(u1_x0, u2_x80) and is_merge_true(u1_y80, l3_y0):
                return '1,3'
            elif is_merge_true(u1_y0, u0_y80) and is_merge_true(u1_x80, l1_x0):
                return '1,4'
            elif is_merge_true(u1_x0, l0_x80) and is_merge_true(u1_y0, l1_y80) and is_merge_true(u1_x80, l2_x0):
                return '1,5'
            elif is_merge_true(u1_x0, l1_x80) and is_merge_true(u1_y0, u2_y80) and is_merge_true(u1_x80, l3_x0):
                return '1,6'
            elif is_merge_true(u1_x0, l2_x80) or is_merge_true(u1_y0, u3_y80):
                return '1,7'
            return None


if __name__ == '__main__':
    x = GapLocater('./images/slider.jpg', './images/captcha.jpg', './images/slide_result.jpg')
    print(x.run())
    #
    # x = get_pos1('./images/exchange.jpg')
    # print(x)
    # print(os.path.dirname(__file__).replace('\\','/'))
