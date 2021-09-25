import os
import re
import redis
import time
import execjs
import requests
import random
import json
from urllib.parse import quote
from utils.proxy import get_ip
import utils.tools as tl
import utils.img_process as imp
from settings import base_settings, save_fail_rush, save_logs, isDebug, redis_db_click
from loguru import logger
import warnings

warnings.filterwarnings("ignore")


class Capt_validate:

    def __init__(self):
        self.session = None
        self.capt_type = None
        self.headers = tl.ua(1)
        self.aes_key = tl.aeskey()  # 唯一aeskey
        self.aes = tl.AESCipher(self.aes_key)
        self.ctx_click = None  # 点选js
        self.slide_track = None  # 滑块轨迹
        # self.proxy = proxy  # 极验不校验IP
        self.pic_type_item = {'phrase': '语序点选', 'icon': '图标点选', 'space': '空间点选', 'word': '文字点选', 'nine': '九宫格点选'}
        # 极验点选缓存池
        click_rush_pool = redis.ConnectionPool(host=redis_db_click['host'], port=redis_db_click['port'],
                                               db=redis_db_click['db'],
                                               decode_responses=True, password=redis_db_click['password'])
        self.click_redis = redis.StrictRedis(connection_pool=click_rush_pool)
        with open('./GeeTest_Click/clicks.js', 'r', encoding='utf-8') as f:
            self.ctx_click = execjs.compile(f.read())
        with open('./rush/slide.json', 'r', encoding='utf-8') as f:
            self.slide_track = json.loads(f.read())

        if save_logs:
            log_path = f'logs/GeeTestLogs_{time.strftime("%Y-%m-%d")}.log'
            logger.add(log_path, rotation="18:30", retention="2 days", enqueue=True)

    def initCaptcha(self,send_data):

        # 初始化，获取js文件
        init_url = f'https://api.geetest.com/gettype.php?gt={send_data["gt"]}&callback=geetest_{int(time.time() * 1000)}'
        init_res = self.session.get(url=init_url, headers=self.headers, proxies=send_data['proxy'], timeout=30).text
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
            "i": "14835!!16140!!CSS1Compat!!1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!2!!3!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!-1!!1!!-1!!-1!!-1!!0!!0!!0!!0!!543!!937!!1920!!1040!!zh-CN!!zh-CN,zh-TW,zh,en-US,en!!-1!!1!!24!!Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36!!1!!1!!1920!!1080!!1920!!1040!!1!!1!!1!!-1!!Win32!!0!!-8!!584f4432fe6ebea605c1f943c0a39f15!!0b03cc6df4e2fc61df0144cad52b685f!!internal-pdf-viewer,mhjfbmdgcfjbbpaeojofohoefgiehjai,internal-nacl-plugin!!0!!-1!!0!!6!!Arial,ArialBlack,ArialNarrow,BookAntiqua,BookmanOldStyle,Calibri,Cambria,CambriaMath,Century,CenturyGothic,CenturySchoolbook,ComicSansMS,Consolas,Courier,CourierNew,Garamond,Georgia,Helvetica,Impact,LucidaBright,LucidaCalligraphy,LucidaConsole,LucidaFax,LucidaHandwriting,LucidaSans,LucidaSansTypewriter,LucidaSansUnicode,MicrosoftSansSerif,MonotypeCorsiva,MSGothic,MSPGothic,MSReferenceSansSerif,MSSansSerif,MSSerif,PalatinoLinotype,SegoePrint,SegoeScript,SegoeUI,SegoeUILight,SegoeUISemibold,SegoeUISymbol,Tahoma,Times,TimesNewRoman,TrebuchetMS,Verdana,Wingdings,Wingdings2,Wingdings3!!1611562895932!!-1!!-1!!-1!!12!!-1!!-1!!-1!!6!!-1!!-1"
        }
        init_res = json.loads(init_res.split('(')[1].split(')')[0])
        init_dict.update(init_res.get('data'))
        if isDebug:
            logger.debug('初始化JS，版本：{}'.format(init_dict))

        # 第一个W
        aes_encoding = self.aes.after_aes(json.dumps(init_dict, ensure_ascii=False), '')
        rsa_encoding = tl.RSA_encrypt(self.aes_key)
        f_w = aes_encoding + rsa_encoding
        url = f'https://api.geetest.com/get.php?gt={send_data["gt"]}&challenge={send_data["challenge"]}&lang=zh-cn&pt=0&client_type=web&w={f_w}&callback=geetest_{int(time.time() * 1000)}'
        res = self.session.get(url=url, headers=self.headers, proxies=send_data["proxy"], timeout=30).text
        res = json.loads(res.split('(')[1].split(')')[0])
        array = res.get('data').get('c')
        s = res.get('data').get('s')
        if isDebug:
            logger.debug('固定数组，第一个随机数：{}    {}'.format(array, s))

        # 处理动态capt_token
        capt_token = self.Token_process(init_dict)

        # 第二个W
        te = "M(n?Nc9MM(mFBB)U-(.O5T.VGi:TK4U)L:11(2Y-,.*ME)c.,IE1(E9(ESW(E3)(M3ZHU(Abb1(1K"
        start = int(time.time()) * 1000 - 10000
        current_time = start - 10000
        model = {
            "lang": "zh-cn",
            "type": "fullpage",
            "tt": tl.s_w_track(te, array, s),
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
            "rp": tl.md5_encrypt(send_data['gt'] + send_data['challenge'] + '9706'),
            "captcha_token": capt_token
        }
        sec_w = self.aes.after_aes(json.dumps(model, ensure_ascii=False), '')
        url = f'https://api.geetest.com/ajax.php?gt={send_data["gt"]}&challenge={send_data["challenge"]}&lang=zh-cn&pt=0&client_type=web&w={sec_w}&callback=geetest_{int(time.time() * 1000)}'
        res = self.session.get(url=url, headers=self.headers, proxies=send_data["proxy"], timeout=30).text
        res = json.loads(res.split('(')[1].split(')')[0])  # 返回验证码类型，直接返回validate则为无感
        types = res.get('data')
        return types

    def Token_process(self, data):
        """ 检测fullpage版本 """
        fullpage_url = 'https://static.geetest.com' + data.get('fullpage')
        try:
            res = self.session.get(url=fullpage_url, headers=self.headers).text
            fun_max = re.findall(';\(function (.*?)\(e,t\)(.*?),new Date\(\)\)\);', res)[0]
            fun_max = 'function ' + fun_max[0] + '(e,t)' + '{' + re.findall('(?<=\{).*(?=\})', fun_max[1])[0] + '}'
            fun_min = re.findall(';function (.*?)\(e\)(.*?)new Date\(\)', fun_max)[0]
            fun_min = 'function ' + fun_min[0] + '(e)' + fun_min[1]
            capt_token = str(tl.Calstr(fun_max + str(tl.Calstr(fun_min)) + str(tl.Calstr('bbOy'))))
            if isDebug:
                logger.success('动态Token：{}'.format(capt_token))
            return capt_token
        except Exception as err:
            logger.error('动态Token处理失败：{}'.format(err))

    def Config(self, send_data, types):

        config_url = f'https://api.geetest.com/get.php?is_next=true&type={types}&gt={send_data["gt"]}&challenge={send_data["challenge"]}&lang=zh-cn&https=false&protocol=https%3A%2F%2F&offline=false&product=embed&api_server=api.geetest.com&isPC=true&width=100%25&callback=geetest_{int(time.time() * 1000)}'
        try:
            config_res = self.session.get(url=config_url, headers=self.headers, proxies=send_data['proxy'], timeout=30).text
            config_res = json.loads(config_res.split('(')[1].split(')')[0])
            if isDebug:
                logger.debug('最后验证所需配置：{}'.format(config_res))
            return config_res
        except Exception as err:
            logger.error('读取配置失败：{}'.format(err.args))

    def Ct_process(self, config):
        """ 检测gct版本 """
        ct_url = 'https://static.geetest.com' + config.get('gct_path')
        try:
            ct_js = self.session.get(url=ct_url, headers=self.headers, timeout=30).text
            fun = re.findall('\[0\];function (.{4})\((.{1})\)(.*?)return function', ct_js)[0]
            fun_1 = 'function ' + fun[0] + f'({fun[1]})' + fun[2].split('function')[0]
            fun_2 = 'function' + 'function'.join(fun[2].split('function')[1:])
            ct_dict = {
                'ct_key': tl.ct_key(ct_js),
                'ct_value': str(tl.Calstr(fun_2 + str(tl.Calstr(fun_1))))
            }
            ct_dict['ct_value'] = tl.ct_outer(ct_dict['ct_key'], ct_dict['ct_value'])
            if isDebug:
                logger.success('动态ct：{}'.format(ct_dict))
            return ct_dict
        except Exception as err:
            logger.error('处理动态ct失败：{}'.format(err.args))

    def CalDistance(self, config):
        """ 图片还原 + 计算距离 + 随机读取轨迹 """
        try:
            res_bg = self.session.get('https://static.geetest.com/' + config["bg"]).content
            bg_arr = imp.img_recover(res_bg)
            res_full = self.session.get('https://static.geetest.com/' + config["fullbg"]).content
            full_arr = imp.img_recover(res_full)
            distance = imp.SlideCrack(bg_arr, full_arr).get_gap() - 5
            slide_list = json.loads(random.choice(self.slide_track[str(distance)]))
            passtime = slide_list[-1][-1]
            if isDebug:
                logger.debug('滑块距离，轨迹，通过时间：{}   {}  {}'.format(distance, slide_list, passtime))
            return {
                'distance': distance,
                'track': slide_list,
                'passtime': passtime
            }
        except Exception as err:
            logger.error('处理图片或生成轨迹失败：{}'.format(err.args))

    def slide_verify(self, verify_dict):
        """ 滑块校验 """
        start = int(time.time()) * 1000 - 10000
        current_time = start - 10000
        track_encrypt = tl.Track(verify_dict['track'])
        full_arr = {
            "lang": "zh-cn",
            "userresponse": tl.user_encrypt(verify_dict['distance'], verify_dict['challenge']),
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
            verify_dict['ct']['ct_key']: verify_dict['ct']['ct_value'],  # 66
            'rp': tl.md5_encrypt((verify_dict["gt"] + verify_dict['challenge'][:32] + str(verify_dict['passtime'])).encode())
        }
        aes_encoding = self.aes.after_aes(json.dumps(full_arr, ensure_ascii=False), '')
        rsa_encoding = tl.RSA_encrypt(self.aes_key)
        third_w = aes_encoding + rsa_encoding
        verify_url = f'https://api.geetest.com/ajax.php?gt={verify_dict["gt"]}&challenge={verify_dict["challenge"]}&lang=zh-cn&pt=0&client_type=web&w={third_w}&callback=geetest_{int(time.time() * 1000)}'
        try:
            verify_res = self.session.get(url=verify_url, headers=self.headers, proxies=verify_dict["proxy"], timeout=30).text
            verify_res = json.loads(verify_res.split('(')[1].split(')')[0])
            return verify_res
        except Exception as err:
            logger.error('验证请求发生错误：{}'.format(err.args))

    def click_verify(self, config):
        """ 点选校验 """
        pic = config['pic']
        c = json.dumps(config['c'], ensure_ascii=False)
        s = config['s']
        pic_type = config['pic_type']

        img_url = 'http://static.geetest.com%s?challenge=%s' % (pic, config['challenge'])
        captcha = self.session.get(headers=self.headers, timeout=30, url=img_url, proxies=config['proxy']).content
        if pic_type == 'space':
            sign = config['sign']
            key = tl.md5_encrypt(str(captcha) + sign)
        else:
            key = tl.md5_encrypt(captcha)
        data = self.click_redis.get(key)  # 读取图片缓存
        if data:
            fail_type = None
            data = data.split('-')
            if pic_type == 'nine':
                points = data
            else:
                points = [str(int(round(int(i.split(',')[0]) / 344 * 10000, 0))) + '_' + str(
                    int(round(int(i.split(',')[1]) / 344 * 10000, 0))) for i in data]
        else:
            """无缓存，打码接口"""
            if pic_type == 'word' or pic_type == 'phrase':
                fail_type = 'Chinese_fail'
                data = imp.chinese_recognize(captcha)
                if not data: return {}
                data = '-'.join([(str(v.get('x')) + ',' + str(v.get('y'))) for v in data.values()])
                data = data.split('-')
                points = [str(int(round(int(i.split(',')[0]) / 344 * 10000, 0))) + '_' + str(
                    int(round(int(i.split(',')[1]) / 344 * 10000, 0))) for i in data]
            elif pic_type == 'nine':
                fail_type = 'Nine_fail'
                data = imp.nine_recognize(captcha)
                if not data: return {}
                data = [i for i in data if i != '']
                points = data
            elif pic_type == 'space':
                fail_type = 'Space_fail'
                sign = config['sign']
                key = tl.md5_encrypt(str(captcha) + sign)
                data = imp.space_recognize(captcha, sign)
                if not data: return {}
                points = [str(int(round(int(i.split(',')[0]) / 344 * 10000, 0))) + '_' + str(
                    int(round(int(i.split(',')[1]) / 344 * 10000, 0))) for i in data]
            elif pic_type == 'icon':
                fail_type = 'Icon_fail'
                data = imp.icon_recognize(captcha)
                if not data: return {}
                points = [str(int(round(int(i.split(',')[0]) / 344 * 10000, 0))) + '_' + str(
                    int(round(int(i.split(',')[1]) / 344 * 10000, 0))) for i in data]
            else:
                logger.warning("未知类型验证码！")
                return config
        points = ','.join(points)
        if isDebug:
            logger.debug(f'GeeTestClick: pic_type: {pic_type} 类型：{self.pic_type_item.get(pic_type)} 加密坐标：{points} ')
        w = self.ctx_click.call('main', points, config['challenge'], config['gt'], pic, c, s, config['ct']['ct_key'],
                                config['ct']['ct_value'])
        if fail_type:
            time.sleep(random.uniform(1.8, 2.3))
        else:
            time.sleep(random.uniform(1.5, 1.8))
        params = {
            'gt': config['gt'],
            'challenge': config['challenge'],
            'lang': 'zh-cn',
            'pt': '3',
            'w': w,
            'callback': 'geetest_%s' % int(time.time() * 1000)
        }
        response = self.session.get(headers=self.headers, url='http://api.geetest.com/ajax.php', params=params,
                                    timeout=30, proxies=config['proxy']).text
        val_items = json.loads(response.split('(')[-1].split(')')[0])
        if val_items['data'].get('validate'):
            if data and fail_type:
                value = '-'.join(data)
                self.click_redis.set(key, value)
            return {
                "challenge": config['challenge'],
                "validate": val_items['data'].get('validate'),
                'click_type': self.pic_type_item.get(pic_type)
            }
        else:
            if data and fail_type and save_fail_rush:
                value = '-'.join(data)
                self.click_redis.set(key, value)
            if base_settings['images_fail_path'] and fail_type:
                save_path = os.path.join(base_settings['images_fail_path'], fail_type)
                tl.save_image(save_path, key, captcha)
            return {}

    def run(self,gt,challenge,proxy):
        retry_count = 0
        while retry_count < 1:
            try:
                self.session = requests.session()
                send_data = {
                    'gt':gt,
                    'challenge':challenge,
                    'proxy':proxy
                }
                s_time = time.time()
                init_data = self.initCaptcha(send_data)
                if init_data.get('validate'):
                    self.capt_type = '无感'
                    res = {
                        'success': True,
                        'message': f'触发{self.capt_type}, 验证成功! ',
                        'data': {
                            'validate': init_data.get('validate'),
                            'challenge': challenge
                        }
                    }
                    logger.debug('识别成功，总计耗时：{}s'.format(float('%.2f' % (time.time() - s_time))))
                    logger.success('识别结果：{}'.format(res))
                    return res
                else:
                    self.capt_type = init_data.get('result')
                    if self.capt_type == 'slide':
                        config = self.Config(send_data,self.capt_type)
                        ct_dict = self.Ct_process(config)
                        verify_dict = self.CalDistance(config)
                        verify_dict.update({
                            'random_s': config.get('s'),
                            'challenge': config.get('challenge'),
                            'array': config.get('c'),
                            'ct': ct_dict,
                            'gt':gt,
                            'proxy':proxy
                        })
                        result = self.slide_verify(verify_dict)
                        if result.get('message') == 'success':
                            res = {
                                'success': True,
                                'message': f'触发{self.capt_type.capitalize()}, 验证成功! ',
                                'data': {
                                    'validate': result.get('validate'),
                                    'challenge': config.get('challenge')
                                }
                            }
                            logger.debug('识别成功，总计耗时：{}s'.format(float('%.2f' % (time.time() - s_time))))
                            logger.success('识别结果：{}'.format(res))
                            return res
                    elif self.capt_type == 'click':
                        config = self.Config(send_data,self.capt_type)
                        config = config.get('data')
                        ct_dict = self.Ct_process(config)
                        config.update({
                            'ct': ct_dict,
                        })
                        config.update(send_data)
                        result = self.click_verify(config)
                        if result.get('validate'):
                            res = {
                                'success': True,
                                'message': f'触发{result.get("click_type")}, 验证成功! ',
                                'data': {
                                    'validate': result.get('validate'),
                                    'challenge': result.get('challenge')
                                }
                            }
                            logger.debug('识别成功，总计耗时：{}s'.format(float('%.2f' % (time.time() - s_time))))
                            logger.success('识别结果：{}'.format(res))
                            return res
                    else:
                        if isDebug:
                            logger.warning('GeeTest异常！')
                        return {'code': 0, 'message': 'Fail', 'data': init_data}
                retry_count += 1
                time.sleep(2)
            except Exception as err:
                if isDebug:
                    logger.error('验证失败，{}'.format(err))
                retry_count += 1
                time.sleep(2)
        return {
            'success': False,
            'message': f'触发{self.capt_type.capitalize()}, 验证失败! ',
            'data': None
        }


def Zd_demo():
    """ 组织机构代码demo """

    query_word = '大渡口小学'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'
    }
    proxy = get_ip()
    session = requests.session()
    query_url = f'https://ss.cods.org.cn/gc/geetest/query?t={int(time.time() * 1000)}'
    query_res = session.get(url=query_url, headers=headers, proxies=proxy).text
    query_res = json.loads(query_res)
    gt = re.findall('"gt":"(.*?)",', query_res)[0]
    challenge = re.findall('"challenge":"(.*?)",', query_res)[0]

    result = Capt_validate().run(gt, challenge, None)
    challenge_ = result.get('data').get('challenge')
    validate_ = result.get('data').get('validate')

    url = f'https://ss.cods.org.cn/latest/searchR?q={quote(quote(query_word))}&t=common&currentPage=1&searchToken=&geetest_challenge={challenge_}&geetest_validate={validate_}&geetest_seccode={validate_}|jordan'
    res = session.get(url=url, headers=headers, proxies=proxy).text
    print(res)


def Geest_demo():
    """ 极验官网demo """

    url = 'https://www.geetest.com/demo/gt/register-slide?t={}'.format(int(time.time() * 1000))
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    res = requests.get(url, headers=headers).json()
    challenge = res.get('challenge')
    gt = res.get('gt')
    result = Capt_validate().run(gt, challenge, None)
    return result


if __name__ == '__main__':
    Zd_demo()
