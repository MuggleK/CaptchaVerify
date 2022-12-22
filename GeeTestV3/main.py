import os
import re
import time
import json
from io import BytesIO

import execjs
import random
import requests
import warnings
import itertools
import ddddocr

from PIL import Image
from loguru import logger

from settings import click_redis, save_logs, isDebug, base_settings
from utils.img_process import img_recover, SlideCrack
from utils.tools import (
    aes_key, AESCipher, rsa_encrypt, s_w_track, md5_encrypt,
    cal_str, ct_key, Track, user_encrypt, save_image, ct_outer, ua
)

warnings.filterwarnings("ignore")


det = ddddocr.DdddOcr(det=True)


class CaptValidate:

    def __init__(self):
        self.capt_type = None
        self.headers = ua(1)
        self.aes_key = aes_key()  # 唯一aes_key
        self.aes = AESCipher(self.aes_key)
        self.ctx_click = None  # 点选js
        self.slide_track = None  # 滑块轨迹
        # self.proxy = proxy  # 极验不校验IP
        self.success = 0
        self.total = 0
        self.success_rush = 0
        self.total_rush = 0
        self.pic_type_item = {'phrase': '语序点选', 'icon': '图标点选', 'space': '空间点选', 'word': '文字点选', 'nine': '九宫格点选'}

        with open('./GeeTest_Click/clicks.js', 'r', encoding='utf-8') as f:
            self.ctx_click = execjs.compile(f.read())
        with open('./geetest_gct_click/source.js', 'r', encoding='utf-8') as f:
            self.ctx_gct = execjs.compile(f.read())
        with open('./rush/slide.json', 'r', encoding='utf-8') as f:
            self.slide_track = json.loads(f.read())

        if save_logs:
            log_path = f'logs/GeeTestLogs_{time.strftime("%Y-%m-%d")}.log'
            logger.add(log_path, rotation="18:30", retention="2 days", enqueue=True)

    def init_captcha(self, send_data: dict, session):
        """
        极验初始化及前两个请求
        :param send_data:
        :param session:
        :return: Geestest Type -> str
        """
        self.total += 1
        # 初始化，获取js文件
        init_url = f'https://api.geetest.com/gettype.php'
        init_params = {
            "gt": send_data["gt"],
            "callback": f"geetest_{int(time.time() * 1000)}"
        }
        init_res = session.get(
            url=init_url,
            params=init_params,
            headers=self.headers,
            proxies=send_data['proxy'],
            timeout=30
        ).text
        init_dict = {
            "gt": send_data['gt'],
            "challenge": send_data['challenge'],
            "offline": False,
            "new_captcha": True,
            "product": "float",
            "width": "300px",
            "https": True,
            "api_server": "apiv6.geetest.com",
            "protocol": "https://",
            "cc": 6,
            "ww": True,
            "i": "14835!!16140!!CSS1Compat!!1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!2!!3!!-1!!-1!!-1!!-1!!-1!!-1!!-1"
                 "!!-1!!-1!!-1!!1!!-1!!-1!!-1!!0!!0!!0!!0!!543!!937!!1920!!1040!!zh-CN!!zh-CN,zh-TW,zh,en-US,"
                 "en!!-1!!1!!24!!Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                 "Chrome/87.0.4280.141 Safari/537.36!!1!!1!!1920!!1080!!1920!!1040!!1!!1!!1!!-1!!Win32!!0!!-8"
                 "!!584f4432fe6ebea605c1f943c0a39f15!!0b03cc6df4e2fc61df0144cad52b685f!!internal-pdf-viewer,"
                 "mhjfbmdgcfjbbpaeojofohoefgiehjai,internal-nacl-plugin!!0!!-1!!0!!6!!Arial,ArialBlack,ArialNarrow,"
                 "BookAntiqua,BookmanOldStyle,Calibri,Cambria,CambriaMath,Century,CenturyGothic,CenturySchoolbook,"
                 "ComicSansMS,Consolas,Courier,CourierNew,Garamond,Georgia,Helvetica,Impact,LucidaBright,"
                 "LucidaCalligraphy,LucidaConsole,LucidaFax,LucidaHandwriting,LucidaSans,LucidaSansTypewriter,"
                 "LucidaSansUnicode,MicrosoftSansSerif,MonotypeCorsiva,MSGothic,MSPGothic,MSReferenceSansSerif,"
                 "MSSansSerif,MSSerif,PalatinoLinotype,SegoePrint,SegoeScript,SegoeUI,SegoeUILight,SegoeUISemibold,"
                 "SegoeUISymbol,Tahoma,Times,TimesNewRoman,TrebuchetMS,Verdana,Wingdings,Wingdings2,"
                 "Wingdings3!!1611562895932!!-1!!-1!!-1!!12!!-1!!-1!!-1!!6!!-1!!-1 "
        }
        init_res = json.loads(init_res.split('(')[1].split(')')[0])
        init_dict.update(init_res.get('data'))

        if isDebug:
            logger.debug('初始化JS，版本：{}'.format(init_dict))

        # 第一个W
        aes_encoding = self.aes.after_aes(json.dumps(init_dict, ensure_ascii=False), '')
        rsa_encoding = rsa_encrypt(self.aes_key)
        f_w = aes_encoding + rsa_encoding
        f_url = f'https://api.geetest.com/get.php'
        f_params = {
            "gt": send_data["gt"],
            "challenge": send_data["challenge"],
            "lang": "zh-cn",
            "pt": 0,
            "client_type": "web",
            "w": f_w,
            "callback": f"geetest_{int(time.time() * 1000)}"
        }
        f_res = session.get(
            url=f_url,
            params=f_params,
            headers=self.headers,
            proxies=send_data["proxy"],
            timeout=30,
        ).text
        f_res = json.loads(f_res.split('(')[1].split(')')[0])

        if f_res.get('status') == 'error':
            logger.warning(f_res)
            return f_res

        array = f_res.get('data').get('c')
        s = f_res.get('data').get('s')

        if isDebug:
            logger.debug('固定数组，第一个随机数：{}    {}'.format(array, s))

        # 处理动态capt_token
        capt_token = self.token_process(init_dict, session)

        # 第二个W
        te = "M(n?Nc9MM(mFBB)U-(.O5T.VGi:TK4U)L:11(2Y-,.*ME)c.,IE1(E9(ESW(E3)(M3ZHU(Abb1(1K"
        start = int(time.time()) * 1000 - 10000
        current_time = start - 10000
        model = {
            "lang": "zh-cn",
            "type": "fullpage",
            "tt": s_w_track(te, array, s),
            "light": "DIV_0",
            "s": "c7c3e21112fe4f741921cb3e4ff9f7cb",
            "h": "25f822388731d727af1e62f164e1eb43",
            "hh": "0a4cc103612378678f48737ba20254cd",
            "hi": "60b1718f6b8bed84a2803a4c7169adcb",
            "vip_order": -1,
            "ct": -1,
            "ep": {
                "v": "9.0.2",
                "de": False,
                "te": False,
                "me": True,
                "ven": "Google Inc.",
                "ren": "ANGLE (Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0)",
                "fp": ["move", 322, 20, start - 5000, "pointermove"],
                "lp": ["up", 345, 337, start - 4000, "pointerup"],
                "em": {
                    "ph": 0,
                    "cp": 0,
                    "ek": "11",
                    "wd": 0,
                    "nt": 0,
                    "si": 0,
                    "sc": 0
                },
                "tm": {'a': current_time,
                       'b': current_time + 258,
                       'c': current_time + 258,
                       'd': 0,
                       'e': 0,
                       'f': current_time + 1,
                       'g': current_time + 4,
                       'h': current_time + 38,
                       'i': current_time + 38,
                       'j': current_time + 166,
                       'k': current_time + 100,
                       'l': current_time + 166,
                       'm': current_time + 256,
                       'n': current_time + 257,
                       'o': current_time + 287,
                       'p': current_time + 538,
                       'q': current_time + 538,
                       'r': current_time + 549,
                       's': current_time + 782,
                       't': current_time + 782,
                       'u': current_time + 782
                       },
                "by": 0
            },
            "passtime": 9706,
            "rp": md5_encrypt((send_data['gt'] + send_data['challenge'] + '9706').encode()),
            "captcha_token": capt_token
        }
        sec_w = self.aes.after_aes(json.dumps(model, ensure_ascii=False), '')
        sec_url = 'https://api.geetest.com/ajax.php'
        sec_params = {
            "gt": send_data["gt"],
            "challenge": send_data["challenge"],
            "lang": "zh-cn",
            "pt": 0,
            "client_type": "web",
            "w": sec_w,
            "callback": f"geetest_{int(time.time() * 1000)}"
        }
        sec_res = session.get(
            url=sec_url,
            params=sec_params,
            headers=self.headers,
            proxies=send_data["proxy"],
            timeout=30
        ).text
        sec_res = json.loads(sec_res.split('(')[1].split(')')[0])  # 返回验证码类型，直接返回validate则为无感
        types = sec_res.get('data')
        return types

    def token_process(self, data, session):
        """
        检测fullpage版本
        :param data:
        :param session:
        :return: capt_token -> str
        """
        # return 106852458
        fullpage_url = 'https://static.geetest.com' + data.get('fullpage')
        try:
            res = session.get(url=fullpage_url, headers=self.headers).text
            fun_max = re.findall(';\\!function (.{1})\\(e,t\\)(.*?),new Date\\(\\)\\)', res)[0]
            fun_max = 'function ' + fun_max[0] + '(e,t)' + '{' + re.findall('(?<=\\{).*(?=\\})', fun_max[1])[0] + '}'
            fun_min = re.findall(";function (.{1})\\(e\\)(.*?)new Date\\(\\)", fun_max)[0]
            fun_min = 'function ' + fun_min[0] + '(e)' + fun_min[1].replace('100<', '')
            capt_token = str(cal_str(fun_max + str(cal_str(fun_min)) + str(cal_str('bbOy'))))  # 最后一个值为动态

            if isDebug:
                logger.success('动态Token：{}'.format(capt_token))

            return capt_token
        except Exception as err:
            logger.error('动态Token处理失败：{}'.format(err))

    def config(self, send_data, types, session):
        """

        :param send_data:
        :param types:
        :param session:
        :return:
        """
        config_url = f'https://api.geetest.com/get.php'
        config_params = {
            "is_next": "true",
            "type": types,
            "gt": send_data["gt"],
            "challenge": send_data["challenge"],
            "lang": "zh-cn",
            "https": "false",
            "protocol": "https://",
            "offline": "false",
            "product": "embed",
            "api_server": "api.geetest.com",
            "isPC": "true",
            "width": "100%",
            "callback": f"geetest_{int(time.time() * 1000)}"
        }
        try:
            config_res = session.get(
                url=config_url,
                params=config_params,
                headers=self.headers,
                proxies=send_data['proxy'],
                timeout=30
            ).text
            config_res = json.loads(config_res.split('(')[1].split(')')[0])

            if isDebug:
                logger.debug('最后验证所需配置：{}'.format(config_res))

            return config_res
        except Exception as err:
            logger.error('读取配置失败：{}'.format(err.args))

    def ct_process(self, config, session):
        """
        检测gct版本
        :param config:
        :param session:
        :return:
        """
        ct_url = 'https://static.geetest.com' + config.get('gct_path')
        try:
            ct_js = session.get(url=ct_url, headers=self.headers, timeout=30).text
            fun = re.findall(';function (.{4})\\(t\\)(.*?)return function', ct_js)[0]
            fun_1 = 'function ' + fun[0] + '(t)' + fun[1].split('function')[0]
            fun_2 = 'function' + fun[1].split('function')[1] + ct_js.split('return function(t)')[0].split(fun[1].split('function')[1])[1] + str(cal_str(fun_1))
            ct_dict = {
                'ct_key': ct_key(ct_js),
                'ct_value': str(cal_str(fun_2))
            }
            ct_value = self.ctx_gct.call('get_ctvalue', ct_dict['ct_key'], ct_dict['ct_value'])
            ct_dict['ct_value'] = ct_value

            if isDebug:
                logger.success('动态ct：{}'.format(ct_dict))

            return ct_dict
        except Exception as err:
            logger.error('处理动态ct失败：{}'.format(err.args))

    def cal_distance(self, config, session):
        """
        图片还原 + 计算距离 + 随机读取轨迹
        :param config:
        :param session:
        :return:
        """
        try:
            res_bg = session.get('https://static.geetest.com/' + config["bg"]).content
            bg_arr = img_recover(res_bg)
            res_full = session.get('https://static.geetest.com/' + config["fullbg"]).content
            full_arr = img_recover(res_full)
            distance = SlideCrack(bg_arr, full_arr).get_gap() - 5
            slide_list = json.loads(random.choice(self.slide_track[str(distance)]))
            pass_time = slide_list[-1][-1]

            if isDebug:
                logger.debug('滑块距离，轨迹，通过时间：{}   {}  {}'.format(distance, slide_list, pass_time))

            return {
                'distance': distance,
                'track': slide_list,
                'passtime': pass_time
            }
        except Exception as err:
            logger.error('处理图片或生成轨迹失败：{}'.format(err.args))

    def slide_verify(self, verify_dict, session):
        """
        滑块校验
        :param verify_dict:
        :param session:
        :return:
        """
        start = int(time.time()) * 1000 - 10000
        current_time = start - 10000
        track_encrypt = Track(verify_dict['track'])
        full_arr = {
            "lang": "zh-cn",
            "userresponse": user_encrypt(verify_dict['distance'], verify_dict['challenge']),
            "passtime": verify_dict['passtime'],
            "imgload": 63,
            "aa": track_encrypt.encrypt(track_encrypt.encrypt1(), verify_dict['array'], verify_dict['random_s']),
            "ep": {
                "v": "7.7.6",
                "te": False,
                "me": True,
                "tm": {'a': current_time,
                       'b': current_time + 258,
                       'c': current_time + 258,
                       'd': 0,
                       'e': 0,
                       'f': current_time + 1,
                       'g': current_time + 4,
                       'h': current_time + 38,
                       'i': current_time + 38,
                       'j': current_time + 166,
                       'k': current_time + 100,
                       'l': current_time + 166,
                       'm': current_time + 256,
                       'n': current_time + 257,
                       'o': current_time + 287,
                       'p': current_time + 538,
                       'q': current_time + 538,
                       'r': current_time + 549,
                       's': current_time + 782,
                       't': current_time + 782,
                       'u': current_time + 782
                       },
                "td": -1,
            },
            verify_dict['ct']['ct_key']: verify_dict['ct']['ct_value'],
            'rp': md5_encrypt(
                (verify_dict["gt"] + verify_dict['challenge'][:32] + str(verify_dict['passtime'])).encode())
        }
        aes_encoding = self.aes.after_aes(json.dumps(full_arr, ensure_ascii=False), '')
        rsa_encoding = rsa_encrypt(self.aes_key)
        third_w = aes_encoding + rsa_encoding
        verify_url = f'https://api.geetest.com/ajax.php'
        verify_params = {
            "gt": verify_dict["gt"],
            "challenge": verify_dict["challenge"],
            "lang": "zh-cn",
            "pt": "0",
            "client_type": "web",
            "w": third_w,
            "callback": f"geetest_{int(time.time() * 1000)}"
        }
        try:
            verify_res = session.get(
                url=verify_url,
                params=verify_params,
                headers=self.headers,
                proxies=verify_dict["proxy"],
                timeout=30
            ).text
            verify_res = json.loads(verify_res.split('(')[1].split(')')[0])
            return verify_res
        except Exception as err:
            logger.error('验证请求发生错误：{}'.format(err.args))

    @staticmethod
    def recognize(captcha):
        imb = Image.new('RGBA', (344, 344), (255, 255, 255, 0))
        picture = Image.open(BytesIO(captcha))
        imb.paste(picture, (0, 0))
        img_byte = BytesIO()
        imb.save(img_byte, format='png')
        poses = det.detection(img_byte.getvalue())
        position = [str(int((i[0] + i[2]) / 2)) + "," + str(int((i[1] + i[3]) / 2)) for i in poses]
        if not position:
            return []
        return position

    def random_position(self, key, captcha):
        try:
            click_redis.llen(key)
            if click_redis.llen(key) == 1:
                return click_redis.llen(key), json.loads(click_redis.rpoplpush(key, key))
        except Exception as err:
            print(err)
            value = click_redis.get(key)
            click_redis.delete(key)

            click_redis.rpush(key, value)
            return 1, json.loads(click_redis.rpoplpush(key, key))

        if click_redis.llen(key) == 1:
            return click_redis.llen(key), json.loads(click_redis.rpoplpush(key, key))
        elif click_redis.llen(key) > 1:
            return click_redis.llen(key), json.loads(click_redis.lpop(key))
        else:
            position = self.recognize(captcha)
        if not position:
            print(f'{key} 未识别到坐标！')
            return None, None

        position_list = [list(i) for i in itertools.permutations(position, len(position))]
        for position in position_list:
            click_redis.lpush(key, json.dumps(position))
        return len(position_list), json.loads(click_redis.lpop(key))

    def click_verify(self, config, session):
        """
        点选校验
        :param config:
        :param session:
        :return:
        """
        pic = config['pic']
        c = json.dumps(config['c'], ensure_ascii=False)
        s = config['s']
        pic_type = config['pic_type']

        img_url = 'http://static.geetest.com%s?challenge=%s' % (pic, config['challenge'])
        captcha = session.get(headers=self.headers, timeout=30, url=img_url, proxies=config['proxy']).content
        if pic_type == 'space':
            sign = config['sign']
            key = pic_type + '_' + md5_encrypt(str(captcha) + sign)
        else:
            key = pic_type + '_' + md5_encrypt(captcha)

        key_len, data = self.random_position(key, captcha)  # 读取图片缓存
        if data:
            logger.info(f'当前尝试{pic_type} key_len:{key_len} key: {key} 坐标：{data}')
            fail_type = None
            self.success_rush += 1
            if pic_type == 'nine':
                points = data
            else:
                points = [str(int(round(int(i.split(',')[0]) / 344 * 10000, 0))) + '_' + str(
                    int(round(int(i.split(',')[1]) / 344 * 10000, 0))) for i in data]
        else:
            return
        points = ','.join(points)

        if isDebug:
            logger.debug(f'GeeTestClick: pic_type: {pic_type} 类型：{self.pic_type_item.get(pic_type)} 加密坐标：{points} ')

        w = self.ctx_click.call('main', points, config['challenge'], config['gt'], pic, c, s, config['ct']['ct_key'],
                                config['ct']['ct_value'])

        time.sleep(random.uniform(2.5, 2.6))
        params = {
            'gt': config['gt'],
            'challenge': config['challenge'],
            'lang': 'zh-cn',
            'pt': '3',
            'w': w,
            'callback': 'geetest_%s' % int(time.time() * 1000)
        }
        response = session.get(
            url='http://api.geetest.com/ajax.php',
            params=params,
            headers=self.headers,
            timeout=30,
            proxies=config['proxy']
        ).text
        val_items = json.loads(response.split('(')[-1].split(')')[0])

        if '网络不给力' in response or val_items.get('error_code'):
            return {}

        if val_items['data'].get('validate'):
            click_redis.delete(key)
            click_redis.rpush(key, json.dumps(data))
            return {
                "challenge": config['challenge'],
                "validate": val_items['data'].get('validate'),
                'click_type': self.pic_type_item.get(pic_type)
            }

        elif val_items['data'].get('result') == 'fail':
            if click_redis.llen(key) == 1:
                click_redis.lpop(key)

        else:
            if base_settings['images_fail_path'] and fail_type:
                save_path = os.path.join(base_settings['images_fail_path'], str(fail_type))
                save_image(save_path, key, captcha)
        return {}

    def run(self, gt, challenge, proxy):
        retry_count = 0
        while retry_count < 2:
            try:
                session = requests.session()
                send_data = {
                    'gt': gt,
                    'challenge': challenge,
                    'proxy': {'http': proxy}
                }
                s_time = time.time()
                init_data = self.init_captcha(send_data, session)

                if not init_data:
                    return

                pic_type = None

                if init_data.get('validate'):
                    self.success += 1
                    pic_type = '无感'
                    res = {'code': 200, 'message': 'success', 'yz_type': pic_type,
                           'data': {
                               'validate': init_data.get('validate'),
                               'challenge': challenge
                           }}

                else:
                    self.capt_type = init_data.get('result')

                    if self.capt_type == 'slide':
                        config = self.config(send_data, self.capt_type, session)
                        pic_type = '滑块'
                        ct_dict = self.ct_process(config, session)
                        verify_dict = self.cal_distance(config, session)
                        verify_dict.update({
                            'random_s': config.get('s'),
                            'challenge': config.get('challenge'),
                            'array': config.get('c'),
                            'ct': ct_dict,
                            'gt': gt,
                            'proxy': proxy
                        })
                        result = self.slide_verify(verify_dict, session)

                        if result.get('message') == 'success':
                            self.success += 1
                            res = {'code': 200, 'message': 'success', 'yz_type': pic_type,
                                   'data': {
                                       'validate': result.get('validate'),
                                       'challenge': config.get('challenge')
                                   }}
                        else:
                            res = {'code': 0, 'message': 'Fail', 'data': None}

                    elif self.capt_type == 'click':
                        config = self.config(send_data, self.capt_type, session)
                        config = config.get('data')
                        if not config:
                            return {'code': 0, 'message': 'Fail', 'data': None}
                        pic_type = self.pic_type_item.get(config['pic_type'])
                        ct_dict = self.ct_process(config, session)
                        config.update({
                            'ct': ct_dict,
                        })
                        config.update(send_data)
                        result = self.click_verify(config, session)

                        if result.get('validate'):
                            self.success += 1
                            res = {'code': 200, 'message': 'success', 'yz_type': pic_type,
                                   'data': {
                                       'validate': result.get('validate'),
                                       'challenge': config.get('challenge')
                                   }}
                        else:
                            res = {'code': 0, 'message': 'Fail', 'data': None}
                    else:
                        res = {'code': 0, 'message': 'type_Fail', 'data': self.capt_type}
                logger.info(
                    f"GeeTest_ACC: {self.success / self.total} total: {self.total} success: {self.success} "
                    f"time_consuming: {float('%.2f' % (time.time() - s_time))}s verify_type: {pic_type}"
                )
                logger.success(f"识别结果：{res}")
                return res
            except Exception as err:
                if isDebug:
                    logger.exception(err)
                    logger.error('验证失败，{}'.format(err))
                retry_count += 1
                time.sleep(2)
        return {
            'success': False,
            'message': f'触发{self.capt_type.capitalize()}, 验证失败! ',
            'data': None
        }
