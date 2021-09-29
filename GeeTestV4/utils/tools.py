import rsa
import random
import re
import math
import hashlib
import binascii
import ctypes
import os
import cv2
import requests
from urllib.parse import unquote
from Crypto.Cipher import AES
from PIL import Image
from io import BytesIO
import numpy as np
from collections import Counter


def aeskey():
    return hex((int(65536 * (1 + random.random())) | 0))[3:] + hex((int(65536 * (1 + random.random())) | 0))[3:] + hex(
        (int(65536 * (1 + random.random())) | 0))[3:] + hex((int(65536 * (1 + random.random())) | 0))[3:]


def RSA_encrypt(aeskey):
    public_key_n = "00C1E3934D1614465B33053E7F48EE4EC87B14B95EF88947713D25EECBFF7E74C7977D02DC1D9451F79DD5D1C10C29ACB6A9B4D6FB7D0A0279B6719E1772565F09AF627715919221AEF91899CAE08C0D686D748B20A3603BE2318CA6BC2B59706592A9219D0BF05C9F65023A21D2330807252AE0066D59CEEFA5F2748EA80BAB81"
    public_key_e = '10001'
    rsa_n = int(public_key_n, 16)
    rsa_e = int(public_key_e, 16)
    key = rsa.PublicKey(rsa_n, rsa_e)
    endata = rsa.encrypt(aeskey.encode(), key)
    endata = binascii.b2a_hex(endata)
    return endata.decode()


def int_overflow(val):
    """
    JS数值处理
    :param val:
    :return:
    """
    maxint = 2147483647
    if not -maxint - 1 <= val <= maxint:
        val = (val + (maxint + 1)) % (2 * (maxint + 1)) - maxint - 1
    return val


def right_shift(n, i):
    # 无符号位运算
    if n < 0:
        n = ctypes.c_uint32(n).value
    if i < 0:
        return -int_overflow(n << abs(i))
    if i != 0:
        return int_overflow(n >> i)
    else:
        return n


class AESCipher:
    def __init__(self, key):
        self.key = key.encode('utf-8')
        self.mode = AES.MODE_CBC

    def encrypt(self, raw):
        """加密"""
        text = raw.encode('utf-8')
        cryptor = AES.new(self.key, self.mode, '0000000000000000'.encode('utf-8'))
        length = 16
        count = len(text)
        if count < length:
            add = (length - count)
            text = text + (chr(add) * add).encode('utf-8')
        elif count > length:
            add = (length - (count % length))
            text = text + (chr(add) * add).encode('utf-8')
        self.ciphertext = cryptor.encrypt(text)
        sigBytes = len(self.ciphertext)
        words = []
        for i in range(0, sigBytes, 4):
            words.append(int.from_bytes(self.ciphertext[i:i + 4], byteorder='big', signed=True))
        S8q = 10
        M5 = []
        D5 = 0
        I5 = words
        while S8q * (S8q + 1) * S8q % 2 == 0 and D5 < sigBytes:
            U0Q = I5[D5 >> 2] >> 24 - D5 % 4 * 8 & 255
            M5.append(U0Q)
            if S8q > 82393:
                S8q = S8q - 10
            else:
                S8q = S8q + 10
            D5 += 1
        return M5

    def sd(self, Z9):
        u2q = 0
        while u2q != 6:
            if u2q == 0:
                U7q = 0
                u2q = 2
                continue
            if u2q == 2:
                w9 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789()";
                if U7q * (U7q + 1) % 2 + 5 and (Z9 < 0 or Z9 >= len(w9)):
                    return "."
                else:
                    return w9[Z9]

    def ae(self, h9, N9):
        return h9 >> N9 & 1

    def after_aes(self, c9, O9):
        """
        老版AES
        :param c9:
        :param O9:
        :return:
        """
        c9 = self.encrypt(c9)
        f2q = 0
        O9 = {'Td': 7274496, 'Ud': 9483264, 'Vd': 19220, 'Wd': 235, 'Xd': 24, 'Sd': '.'}
        while f2q != 10:
            if f2q == 26:
                e9 = None
                f2q = 15
                continue
            if f2q == 24:
                # return {
                #     'res': l9,
                #     'end': n9
                # }
                return l9 + n9
            if f2q == 34:
                if 2 == C9:
                    e9 = (c9[u9] << 16) + (c9[u9 + 1] << 8)
                    l9 += self.sd(b9(e9, O9["Td"])) + self.sd(b9(e9, O9["Ud"])) + self.sd(b9(e9, O9["Vd"]))
                    n9 = O9["Sd"]
                else:
                    if 1 == C9:
                        e9 = c9[u9] << 16
                        l9 += self.sd(b9(e9, O9["Td"])) + self.sd(b9(e9, O9["Ud"]))
                        n9 = O9["Sd"] + O9["Sd"]
                f2q = 30
                continue
            if f2q == 3:
                C9 = a9 % 3
                f2q = 34
                continue
            if f2q == 18:
                u9 += 3
                f2q = 9
                continue
            if f2q == 6:
                def b9(x9, V9):
                    L2q = 0
                    while L2q != 26:
                        if L2q == 0:
                            o9 = 0
                            s9 = O9["Xd"] - 1
                            L2q = 2
                            continue
                        if L2q == 11:
                            if 1 == self.ae(V9, s9):
                                o9 = (o9 << 1) + self.ae(x9, s9)
                            L2q = 6
                            continue
                        if L2q == 6:
                            s9 -= 1
                            L2q = 2
                            continue
                        if L2q == 9:
                            return o9
                        if L2q == 2:
                            if s9 >= 0:
                                L2q = 11
                            else:
                                L2q = 9

                l9 = ""
                n9 = ""
                a9 = len(c9)
                u9 = 0
                f2q = 9
                continue
            if f2q == 0:
                O7q = 0
                if not O9:
                    O9 = {}
                f2q = 6
                continue
            if f2q == 15:
                if u9 + 2 < a9:
                    f2q = 33
                else:
                    f2q = 3
            if f2q == 30:
                if O7q >= 25198:
                    O7q = O7q / 1
                else:
                    O7q = O7q * 1
                f2q = 18
                continue
            if f2q == 33:
                e9 = (c9[u9] << 16) + (c9[u9 + 1] << 8) + c9[u9 + 2]
                l9 += self.sd(b9(e9, O9["Td"])) + self.sd(b9(e9, O9["Ud"])) + self.sd(b9(e9, O9["Vd"])) + self.sd(
                    b9(e9, O9["Wd"]))
                f2q = 30
                continue
            if f2q == 9:
                if u9 < a9 and O7q * (O7q + 1) % 2 + 8:
                    f2q = 26
                else:
                    f2q = 24
                continue

    def new_after_aes(self, c9):
        """
        新版AES 主要区别在于对加密后数组的处理
        :param c9:
        :return:
        """
        e = self.encrypt(c9)
        t = [None for i in range(len(e))]
        s = 0
        for a in range(0, len(e) * 2, 2):
            if t[right_shift(a, 3)]:
                j = t[right_shift(a, 3)] | int(e[s]) << 24 - a % 8 * 4
                t[right_shift(a, 3)] = j if j < 2147483647 else int_overflow(j)
            else:
                t[right_shift(a, 3)] = int(e[s]) << 24 - a % 8 * 4
            s += 1
        t = [i for i in t if i]
        o = []
        for n in range(len(e)):
            r = right_shift(t[right_shift(n, 2)], 24 - n % 4 * 8) & 255
            o.append(hex(right_shift(r, 4))[2:])
            o.append(hex(15 & r)[2:])
            if n == 718:
                pass
        return ''.join(o)


def Calstr(str):
    """检测fullpage和gct核心算法"""
    t = 5381
    r = len(str)
    for i in range(r):
        t = (t << 5) + t + ord(str[i])
    t = t & 2147483647
    return t


def ct_key(ct_res):
    """处理动态gct的key值"""
    str1 = unquote(re.findall("=decodeURI\('(.*?)'\);", ct_res, re.S)[0].replace('\\', ''))
    str2 = re.findall("break;\}\}\}\('(.*?)'\)};break;", ct_res, re.S)[0]
    ind = int(re.findall(";'use strict';var .{1}=.{4}\((.*?)\);", ct_res)[0])
    str3 = ''
    j = 0
    for i in range(len(str1)):
        str3 += chr(ord(str1[i]) ^ ord(str2[j]))
        j += 1
        if j == len(str2):
            j = 0
    decrypt_list = str3.split('^')
    return decrypt_list[ind]


def ct_outer(ct_key, ct_value):
    """
    gct key值最外层加密
    :param ct_key:
    :param ct_value:
    :return:
    """
    ct_val_list = list(ct_value)
    fun_num_map = {
        'n': 5,
        's': 1,
        'e': 3,
        'es': 2,
        'en': 4,
        'w': 7,
        'wn': 6,
        'ws': 8
    }
    fun_name_list = list(fun_num_map.keys())
    s = 70
    o = len(fun_name_list) - 2
    for a in range(len(ct_key)):
        _ = str(abs(ord(ct_key[a]) - s))[1]
        l = int(str(abs(ord(ct_key[a]) - s))[0])
        lastVal = int(ct_val_list[len(ct_val_list) - 1])   # 运算数
        if int(_) > o:
            cal_num = fun_num_map[fun_name_list[o + 1]]
        else:
            cal_num = fun_num_map[fun_name_list[int(_)]]

        if cal_num == 8:
            for __ in range(l):
                ct_val_list[cal_num] = str(int(ct_val_list[cal_num]) * lastVal)
                ct_val_list[cal_num] = str(int(ct_val_list[cal_num]) + lastVal)
                ct_val_list[cal_num] = str(int(ct_val_list[cal_num]) + lastVal)
        elif cal_num == 5:
            for __ in range(l):
                ct_val_list[cal_num] = str(int(ct_val_list[cal_num]) * lastVal)
                ct_val_list[cal_num] = str(int(ct_val_list[cal_num]) * lastVal)
        elif cal_num == 4:
            for __ in range(l):
                ct_val_list[cal_num] = str(int(ct_val_list[cal_num]) + lastVal)
                ct_val_list[cal_num] = str(int(ct_val_list[cal_num]) * lastVal)
        elif cal_num == 1:
            for __ in range(l):
                ct_val_list[cal_num] = str(int(ct_val_list[cal_num]) + lastVal)
                ct_val_list[cal_num] = str(int(ct_val_list[cal_num]) + lastVal)
                ct_val_list[cal_num] = str(int(ct_val_list[cal_num]) + lastVal)
        elif cal_num == 7:
            for __ in range(l):
                ct_val_list[cal_num] = str(int(ct_val_list[cal_num]) * lastVal)
                ct_val_list[cal_num] = str(int(ct_val_list[cal_num]) + lastVal)
        elif cal_num == 3:
            for __ in range(l):
                ct_val_list[cal_num] = str(int(ct_val_list[cal_num]) + lastVal)
                ct_val_list[cal_num] = str(int(ct_val_list[cal_num]) * lastVal)
                ct_val_list[cal_num] = str(int(ct_val_list[cal_num]) + lastVal)
        elif cal_num == 2:
            for __ in range(l):
                ct_val_list[cal_num] = str(int(ct_val_list[cal_num]) + lastVal)
                ct_val_list[cal_num] = str(int(ct_val_list[cal_num]) + lastVal)
        else:
            for __ in range(l):
                ct_val_list[cal_num] = str(int(ct_val_list[cal_num]) * lastVal)
                ct_val_list[cal_num] = str(int(ct_val_list[cal_num]) * lastVal)
                ct_val_list[cal_num] = str(int(ct_val_list[cal_num]) + lastVal)

    return ''.join(ct_val_list)[:10]


def s_w_track(te, array, s):
    v4B = 'abc'
    while v4B != '':
        if v4B == 'abc':
            v8h = 7
            B8h = 1
            v4B = 'def'
        if v4B == 'def':
            if B8h * (B8h + 1) * B8h % 2 == 0 and (not array or not s):
                v4B = 'err'
            else:
                v4B = 'hij'
        if v4B == 'hij':
            F3Q = 0
            M3Q = 0
            p3Q = te
            O3Q = array[0]
            a3Q = array[2]
            Q3Q = array[4]
            v4B = 'klm'
        if v4B == 'klm':
            F3Q = s[M3Q:M3Q + 2]
            if F3Q and v8h * (v8h + 1) * v8h % 2 == 0:
                v4B = 'nop'
            else:
                v4B = 'qrs'
        if v4B == 'nop':
            M3Q += 2
            Z3Q = eval('0x' + F3Q)
            N5f = chr(Z3Q % 256)
            J3Q = (O3Q * Z3Q * Z3Q + a3Q * Z3Q + Q3Q) % len(te)
            v4B = 'tuv'
        if v4B == 'tuv':
            p3Q = p3Q[0:J3Q] + N5f + p3Q[J3Q:]
            v4B = 'wxy'
        if v4B == 'wxy':
            if v8h >= 64237:
                v8h = v8h - 1
            else:
                v8h = v8h + 1
            v4B = 'klm'
        if v4B == 'qrs':
            return p3Q
        if v4B == 'err':
            return te


class Track:
    def __init__(self, track):
        self.track = track

    def encrypt1(self):
        def e(e):
            t = []
            r = 0
            n = None
            i = None
            for a in range(len(e) - 1):
                n = math.ceil(e[a + 1][0] - e[a][0])
                i = math.ceil(e[a + 1][1] - e[a][1])
                o = math.ceil(e[a + 1][2] - e[a][2])
                if n == 0 and i == 0 and o == 0:
                    continue
                if n == 0 and i == 0:
                    r += o
                else:
                    t.append([n, i, o + r])
                    r = 0
            if r != 0:
                t.append([n, i, r])
            return t

        def r(e):
            t = "()*,-./0123456789:?@ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqr"
            r = len(t)
            n = ""
            i = abs(e)
            o = int(i / r)
            if o >= r:
                o = r - 1
            if o:
                n = t[o]
            i = i % r
            a = ""
            if e < 0:
                a += "!"
            if n:
                a += "$"
            return a + n + t[i]

        def n(e):
            t = [[1, 0], [2, 0], [1, -1], [1, 1], [0, 1], [0, -1], [3, 0], [2, -1], [2, 1]]
            r = "stuvwxyz~"
            for n in range(len(t)):
                if e[0] == t[n][0] and e[1] == t[n][1]:
                    return r[n]
            return 0

        self.track = e(self.track)
        i = []
        o = []
        a = []
        for e in self.track:
            t = n(e)
            if t == 0:
                i.append(r(e[0]))
                o.append(r(e[1]))
            else:
                o.append(t)

            a.append(r(e[2]))
        return "".join(i) + "!!" + "".join(o) + "!!" + "".join(a)

    def encrypt(self, e, t, r):
        if not t or not r:
            return e
        n = 0
        i = 2
        a = e
        s = t[0]
        u = t[2]
        c = t[4]
        while n < len(r):
            o = r[n:n + 2]
            _ = int(o, 16)
            f = chr(_)
            l = (s * _ * _ + u * _ + c) % len(e)
            a = a[0:l] + f + a[l:]
            n += i
        return a


def md5_encrypt(x):
    n = hashlib.md5()
    n.update(x)
    return n.hexdigest()


def user_encrypt(e, t):
    """老版user_response加密"""
    r = t[-2:]
    n = [None, None]
    for i in range(len(r)):
        o = ord(r[i])
        if o > 57:
            n[i] = o - 87
        else:
            n[i] = o - 48
    r = n[0] * 36 + n[1]
    a = math.ceil(e) + r
    t = t[:32]
    s = [[], [], [], [], []]
    u = {}
    c = 0
    i = 0
    for i in range(len(t)):
        _ = t[i]
        if not u.get(_):
            u[_] = 1
            s[c].append(_)
            c += 1
            if c == 5:
                c = 0
    l = a
    v = 4
    d = ""
    p = [1, 2, 5, 10, 50]
    while l > 0:
        if l - p[v] >= 0:
            h = int(random.random() * len(s[v]))
            d = d + s[v][h]
            l = l - p[v]
        else:
            del s[v]
            del p[v]
            v = v - 1
    return d


def uuid():
    """
    随机challenge
    :return:
    """
    encrypt_str = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'
    uuid_ = ''
    for i in encrypt_str:
        if i == 'x' or i == 'y':
            r = math.floor(random.random() * 16)
            if i == 'x':
                v = r
            elif i == 'y':
                v = r & 0x3 | 0x8
            uuid_ += hex(v)[2:]
        else:
            uuid_ += i
    return uuid_


def get_track(distance):
    """
    滑动长度 >= 200 自写算法
    :param distance:
    :return:
    """
    track_init = [[random.randint(-40, -25), random.randint(-40, -25), 0], [0, 0, 0]]
    track_list = []
    x_f = 0
    time_start = random.randint(200, 277)
    while x_f <= distance:
        track = []
        x_f += random.randint(0, 4)
        track.append(x_f)
        track.append(random.randint(-1, 1))
        time_start += random.randint(6, 30)
        track.append(time_start)
        track_list.append(track)
    track_list = track_init + track_list
    return track_list


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
    :param type:
    :return:
    """
    img_data = requests.get(url, proxies=ip).content
    content = img_data
    return content


def get_distance(slider_url, captcha_url, ip):
    """
    获取缺口距离
    :param slider_url: 滑块图片 url
    :param captcha_url: 验证码图片 url
    :return:
    """
    # save_path = os.path.dirname(__file__).replace('\\','/') + '/images'
    # if not os.path.exists(save_path):
    #     os.mkdir(save_path)

    # 引用上面的图片下载
    slider_content = _pic_download(slider_url, ip)

    # 引用上面的图片下载
    captcha_content = _pic_download(captcha_url, ip)
    img_size = Image.open(BytesIO(captcha_content)).size
    if slider_content and captcha_content:
        distance = GapLocater(slider_content, captcha_content).run(True)[0] + 3

        return distance, img_size[0]
    return 0, 0


def condition_icon(transfer_ques):
    for index_ques, i in enumerate(transfer_ques):
        val_counter = dict(Counter(i))
        contains_index = None
        jj = None
        for key, value in val_counter.items():
            if value > 1:
                jj = key
                range_3 = list(range(0, 3))
                is_ind = []
                for index, key_ in enumerate(i):
                    if key_ == key:
                        is_ind.append(index)
                contains_index = list(set(range_3) - set(is_ind))[0]
        if contains_index is not None:
            if index_ques == 0:
                compare_index = index_ques + 1
            elif index_ques == 1:
                compare_index = [index_ques + 1, index_ques - 1]
            else:
                compare_index = index_ques - 1
            if isinstance(compare_index, int):
                if transfer_ques[compare_index][contains_index] == jj:
                    return [[index_ques, contains_index],
                            [compare_index, contains_index]]
            else:
                if transfer_ques[compare_index[0]][contains_index] == jj:
                    return [[index_ques, contains_index],
                            [compare_index[0], contains_index]]
                if transfer_ques[compare_index[1]][contains_index] == jj:
                    return [[index_ques, contains_index],
                            [compare_index[1], contains_index]]


def match_icon(ques):
    """
    消消乐坐标检测
    :param ques:
    :return:
    """
    transfer_ques = list(map(list, zip(*ques)))
    # for i, j, k in transfer_ques:
    #     print(i, j, k)
    # print('==' * 100)
    transfer_ques_ = list(map(list, zip(*transfer_ques)))
    res = condition_icon(transfer_ques)
    if res:
        res = [[res[0][1], res[0][0]], [res[1][1], res[1][0]]]
        return res
    else:
        res = condition_icon(transfer_ques_)
        return res


def five_points(ques):
    """
    五子棋坐标检测
    :param ques:
    :return:
    """
    # for i, j, k, m, n in ques:
    #     print(i, j, k, m, n)
    # print('==' * 100)
    total_list = [j for i in ques for j in i]
    five_count = dict(Counter(total_list))
    five_val_list = []
    for key, val in five_count.items():
        if val == 5:
            five_val_list.append(key)
    for five_val in five_val_list:
        # 找出 出现刚好5次数字的坐标
        points_list = []
        for index_ques, i in enumerate(ques):
            for inde_i, i_val in enumerate(i):
                if i_val == five_val:
                    points_list.append([index_ques, inde_i])

        # 根据特征匹配坐标
        # print(points_list)
        y_most = Counter([i[1] for i in points_list]).most_common()
        x_most = Counter([i[0] for i in points_list]).most_common()
        if y_most[0][1] == 4:
            # 纵坐标一致
            move_point = [i for i in points_list if i[1] != y_most[0][0]][0]
            points_list.remove(move_point)
            point_x = list(set(list(range(5))) - set([i[0] for i in points_list]))[0]
            res = [move_point, [point_x, y_most[0][0]]]
        elif x_most[0][1] == 4:
            # 横坐标一致
            move_point = [i for i in points_list if i[0] != x_most[0][0]][0]
            points_list.remove(move_point)
            point_y = list(set(list(range(5))) - set([i[1] for i in points_list]))[0]
            res = [move_point, [x_most[0][0], point_y]]
        else:
            # 斜
            h_list = [[0, 0], [1, 1], [2, 2], [3, 3], [4, 4]]
            z_list = [[0, 4], [1, 3], [2, 2], [3, 1], [4, 0]]
            h_list_ = [i for i in points_list if i not in h_list]
            z_list_ = [i for i in points_list if i not in z_list]
            if len(h_list_) == 1:
                move_point = h_list_[0]
                points_list.remove(move_point)
                other_point = [i for i in h_list if i not in points_list][0]
                res = [move_point,other_point]
            elif len(z_list_) == 1:
                move_point = z_list_[0]
                points_list.remove(move_point)
                other_point = [i for i in z_list if i not in points_list][0]
                res = [move_point, other_point]
            else:
                res = []
        if res:
            return res


def sort_points(center_points, new_points, end_center_point):
    new_points.append(end_center_point)
    center_points_ = np.array(center_points)
    if len(center_points_) == 0:
        return new_points
    points_distances = center_points_ - end_center_point
    points_length = []
    for points_distance in points_distances:
        points_length.append(int(np.sqrt(np.square(points_distance[0]) + np.square(points_distance[1]))))
    min_arg = np.argmin(points_length)
    current_end_center_point = center_points[min_arg]
    center_points.remove(center_points[min_arg])
    new_points = sort_points(center_points, new_points, current_end_center_point)
    return new_points


def fp_trace(img_content):
    """
    四代手势轨迹解析
    :param img_content: 图片二进制流
    :return:
    """
    image = cv2.imdecode(np.frombuffer(img_content, np.uint8), 1)
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image_gray[image_gray > 180] = 255
    image_gray[image_gray < 150] = 255
    image_gray[image_gray < 200] = 0

    image_bw = cv2.dilate(image_gray, np.ones((2, 2), dtype=np.uint8))
    image_erode_3 = cv2.erode(image_bw, np.ones((3, 3), dtype=np.uint8))

    contours, _ = cv2.findContours(255 - image_erode_3, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    areas = []
    center_points = []
    for i, cnt in enumerate(contours):
        areas.append(cv2.contourArea(cnt))
        x, y, w, h = cv2.boundingRect(cnt)
        center_points.append([y + h // 2, x + w // 2])
    x, y, w, h = cv2.boundingRect(contours[np.argmax(areas)])
    end_center_point = center_points[np.argmax(areas)]

    new_points = []
    center_points.remove(end_center_point)
    new_points = sort_points(center_points, new_points, end_center_point)
    new_points.reverse()
    new_points = [list(reversed(i)) for i in new_points]

    # trace
    fpTrace = []
    fpTrace.append(new_points[0] + [0])
    fpTrace.append([0, 0, 0])

    init_timestamp = random.randint(77, 267)
    for point in new_points[1:]:
        init_timestamp += random.randint(7, 19)
        point[0] = round(point[0] / 300, 2)
        point[1] = round(point[1] / 260, 2)
        point += [init_timestamp]
        fpTrace.append(point)
    fpTrace[-1][-1] += random.randint(57, 235)
    return fpTrace


if __name__ == '__main__':
    init_json = {"status": "success", "data": {"lot_number":"4965a642d219473eac9d5ce07fb4b425","captcha_type":"winlinze","js":"/js/gcaptcha4.js","css":"/css/gcaptcha4.css","static_path":"/v4/static/v1.3.5","imgs":["/nerualpic/v4_test/v4_winlinze_test/img_winlinze_0.png","/nerualpic/v4_test/v4_winlinze_test/img_winlinze_1.png","/nerualpic/v4_test/v4_winlinze_test/img_winlinze_2.png","/nerualpic/v4_test/v4_winlinze_test/img_winlinze_3.png","/nerualpic/v4_test/v4_winlinze_test/img_winlinze_4.png"],"ques":[[0,0,3,0,2],[0,0,2,2,0],[3,0,0,0,1],[0,2,0,0,0],[2,0,0,0,0]],"gct_path":"/v4/gct/gct4.4b7d9deafd4e2d0c123e306a23fb231b.js","feedback":"http://www.geetest.com/contact#report","logo":True,"pt":"1","captcha_mode":"risk_manage","custom_theme":{"_style":"stereoscopic","_color":"hsla(224,98%,66%,1)","_gradient":"linear-gradient(180deg, hsla(224,98%,71%,1) 0%, hsla(224,98%,66%,1) 100%)","_hover":"linear-gradient(180deg, hsla(224,98%,66%,1) 0%, hsla(224,98%,71%,1) 100%)","_brightness":"light","_radius":"4px"}}}
    print(five_points([[1, 1, 4, 0, 2], [1, 0, 1, 4, 2], [0, 2, 1, 0, 2], [0, 0, 4, 0, 2], [3, 4, 0, 4, 0]]))
    # aes_key = "9975b62615362a14"
    # aes = AESCipher(aes_key)
    # aes_encoding = aes.new_after_aes(
    #     '{"setLeft":192,"track":[[-40,-31,0],[0,0,0],[1,0,162],[3,0,171],[4,0,177],[6,0,183],[7,0,192],[8,0,199],[11,0,207],[14,0,216],[17,0,223],[20,0,232],[23,0,239],[26,0,247],[29,0,255],[31,0,264],[32,0,272],[34,0,279],[38,0,288],[41,0,296],[44,0,305],[48,0,311],[54,1,322],[61,1,328],[66,1,337],[72,2,344],[77,3,353],[81,3,360],[84,3,369],[94,4,379],[102,5,387],[107,5,393],[113,5,404],[116,5,409],[119,5,416],[122,5,424],[124,6,432],[125,6,439],[128,6,452],[131,7,457],[136,7,468],[139,7,471],[142,7,479],[144,8,488],[146,8,495],[149,8,506],[152,8,513],[154,8,522],[155,8,529],[157,8,538],[159,8,544],[160,9,561],[161,9,576],[162,9,586],[164,9,591],[165,9,600],[166,9,608],[167,9,621],[168,9,637],[169,9,721],[170,9,736],[171,9,743],[172,9,760],[173,9,767],[174,9,792],[175,9,816],[176,9,856],[177,9,896],[178,9,903],[179,9,927],[180,9,951],[181,9,1023],[182,9,1031],[183,9,1047],[184,9,1097],[185,9,1146],[186,9,1151],[187,9,1178],[188,9,1279],[189,10,1328],[190,10,1351],[191,10,1425],[191,10,1840]],"passtime":1840,"userresponse":190.86498952893461,"geetest":"captcha","lang":"zh","ep":"123","gq2x":"418133283","em":{"ph":0,"cp":0,"ek":"11","wd":1,"nt":0,"si":0,"sc":0}}'
    # )
    # print(aes_encoding)
    # print(RSA_encrypt(aes_key))
    # # print(131072 ^ 3489660928)
    # # print(int_overflow(3489792000))
    # # tt = Track([[-34, -39, 0], [0, 0, 0], [1, 1, 91], [3, 1, 99], [4, 1, 116], [8, 1, 123], [9, 1, 131], [11, 1, 139],
    # #             [12, 1, 147], [14, 1, 156], [16, 1, 163], [19, 2, 171], [21, 3, 180], [22, 3, 187], [23, 3, 196],
    # #             [25, 3, 203], [26, 3, 211], [27, 3, 229], [29, 3, 235], [30, 3, 243], [32, 3, 251], [33, 3, 259],
    # #             [34, 3, 275], [34, 4, 283], [35, 4, 291], [36, 4, 323], [37, 4, 339], [38, 4, 347], [39, 4, 363],
    # #             [40, 4, 371], [41, 4, 387], [42, 4, 403], [44, 4, 427], [45, 4, 445], [46, 4, 452], [47, 4, 461],
    # #             [49, 4, 469], [50, 4, 483], [50, 4, 572]])
    # # print(tt.encrypt(tt.encrypt1(), [12, 58, 98, 36, 43, 95, 62, 15, 12], "4a347e6b"))
    # # print(user_encrypt(79, "9107aa61dab48b7c101c23a35fd87fabkm"))
    # # strs_ = "function PpOj(t){var Xkc=AFeaN.EBN()[2][8];for(;Xkc!==AFeaN.EBN()[6][6];){switch(Xkc){case AFeaN.EBN()[4][8]:var r=5381;var e=t[Eipg(1)];var n=0;Xkc=AFeaN.EBN()[6][7];break;case AFeaN.EBN()[2][7]:while(e--){r=(r<<5)+r+t[FjuN(39)](n++);}r&=~(1<<31);return r;break;}}}"
    # # print(Calstr(strs_))
    # new_track = []
    # track = '[[-40, -36, 0], [0, 0, 0], [1, 0, 110], [2, 0, 118], [3, 0, 126], [4, 0, 150], [4, -1, 166], [5, -1, 190], [6, -1, 198], [7, -1, 214], [9, -1, 222], [10, -2, 230], [11, -2, 241], [13, -3, 247], [14, -3, 254], [15, -3, 262], [16, -3, 270], [17, -4, 286], [18, -4, 294], [19, -4, 302], [21, -5, 310], [22, -5, 318], [24, -5, 325], [25, -5, 335], [28, -5, 342], [30, -5, 350], [32, -5, 357], [35, -5, 366], [38, -5, 374], [40, -5, 382], [43, -5, 390], [45, -5, 398], [48, -5, 406], [51, -5, 414], [55, -5, 422], [58, -5, 430], [61, -5, 438], [63, -5, 446], [64, -5, 454], [66, -5, 462], [68, -5, 470], [71, -5, 477], [74, -5, 485], [77, -6, 494], [81, -6, 502], [84, -6, 510], [84, -6, 518], [86, -6, 526], [89, -6, 533], [92, -6, 542], [93, -6, 549], [94, -6, 558], [97, -6, 565], [98, -6, 574], [100, -6, 582], [101, -6, 590], [102, -6, 598], [104, -6, 606], [105, -6, 614], [106, -6, 622], [106, -5, 631], [107, -5, 638], [108, -5, 646], [109, -5, 654], [111, -5, 662], [113, -5, 670], [114, -5, 686], [115, -5, 694], [117, -5, 709], [118, -5, 727], [120, -5, 734], [121, -5, 742], [122, -5, 750], [124, -5, 758], [125, -5, 774], [126, -5, 790], [127, -5, 798], [128, -5, 806], [129, -5, 822], [130, -5, 830], [131, -5, 838], [132, -5, 845], [133, -5, 854], [134, -5, 863], [135, -5, 870], [136, -5, 885], [136, -4, 894], [137, -4, 910], [138, -4, 918], [139, -4, 926], [139, -3, 934], [141, -3, 942], [142, -3, 958], [143, -3, 966], [144, -3, 977], [145, -3, 982], [146, -3, 990], [148, -3, 1007], [149, -3, 1022], [151, -3, 1030], [153, -3, 1046], [154, -3, 1062], [155, -3, 1078], [156, -3, 1094], [157, -3, 1102], [158, -3, 1110], [159, -3, 1126], [160, -3, 1142], [161, -3, 1158], [162, -3, 1182], [163, -3, 1214], [165, -3, 1230], [166, -3, 1253], [167, -3, 1278], [168, -3, 1302], [169, -3, 1310], [170, -3, 1326], [171, -3, 1341], [172, -3, 1358], [173, -3, 1375], [174, -3, 1398], [175, -3, 1422], [176, -3, 1454], [177, -3, 1518], [178, -3, 1574], [179, -3, 1590], [180, -3, 1599], [181, -3, 1606], [182, -3, 1630], [183, -3, 1711], [184, -3, 1726], [184, -3, 2030]]'
    # aa = [i.strip().replace('[','').replace(']','') for i in re.findall('\[(.*?)\]',track)]
    # for i in aa:
    #     jj = [int(j) for j in i.split(',')]
    #     new_track.append(jj)
    # print(new_track)
