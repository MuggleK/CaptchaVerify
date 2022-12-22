# -*- coding: utf-8 -*-
# @Project : Yidun
# @Time    : 2022/11/29 16:22
# @Author  : MuggleK
# @File    : yidun_out.py

import random
import requests
import json
import time
import execjs
import base64
from urllib.parse import urlparse

from util.img_locate import _pic_download, _get_distance
import warnings

from util.settings import (
    dom_js, encrypt_js, core_ctx, captcha_type, dxtubiao_api, fingerprint_ctx, watchman_ctx
)
from util.tools import B, C, str_to_dict, get_proxies
from loguru import logger

warnings.filterwarnings("ignore")


class YidunCracker:

    ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'

    def __init__(self, site, sid, width, referer, host):
        # 调用站点
        self.site = site
        # 调用站点的 id
        self.sid = sid
        # 固定校验类型
        self.type = None
        self.xtype = None
        # 验证码的前置页面, 很重要, 严格站点校验该参数
        self.referer = referer
        self.token = ""
        # 验证码图片在浏览器上的宽
        self.width = int(width)

        # acToken 校验
        self.initWatchman = False
        self.pn = ""
        self.v = ""
        self.random_time = ''
        self.luv = ""
        self.conf = ""
        self.wm_tid = ""
        self.wm_did = ""
        self.wm_ni = ""
        self.wm_nike = ""
        self.ac_token = ""

        # 协议域名解析
        self.protocol = self.referer.split('://')[0]
        self.host = host
        self.local_referer = '/'.join(self.referer.split("/")[:3]) + "/"

        # 指纹缓存
        self.fp = None

        self.session = requests.session()
        self.api_count = 0
        self.proxy = None

    def req_referer(self):
        """
        请求前置页面
        :return:
        """
        self.session.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'max-age=0',
            'Host': self.referer.split('/')[2],
            'Referer': f'{self.protocol}://{self.referer.split("/")[2]}/',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.ua
        }
        self.session.get(self.referer, proxies=self.proxy, timeout=5)

    def process_watchman_js(self):
        """
        处理 watchman js  版本更新需对应特定版本改写
        :return:
        """
        global watchman_ctx
        if watchman_ctx: return
        logger.debug(f"watchman_{self.v} 版本不存在,正在保存至本地")
        watchman_js_url = f'{self.protocol}://acstatic-dun.126.net/{self.v}/watchman.min.js'
        self.session.headers = {
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate',
            'Host': urlparse(watchman_js_url).netloc,
            'Referer': self.local_referer,
            'User-Agent': self.ua
        }
        watchman_code = self.session.get(watchman_js_url, timeout=5).text
        with open("./static/source_watchman.js", "w", encoding="utf-8")as w:
            w.write(watchman_code)
        watchman_ctx = execjs.compile(dom_js + watchman_code + encrypt_js)

    def get_wm_did(self):
        """
        协议获取 wm_did
        :return:
        """
        # url = f"https://{self.host}/v3/d"
        url = "https://webzjac.reg.163.com/v3/d"    # 特殊站点需替换host
        d = watchman_ctx.call('get_dd', self.protocol, self.pn, self.v, self.luv, self.conf)
        data = str_to_dict(d["post_data"])
        self.session.headers = {
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate',
            'Content-type': 'application/x-www-form-urlencoded',
            'Host': urlparse(url).netloc,
            'Referer': self.local_referer,
            'User-Agent': self.ua
        }
        resp = self.session.post(url=url, data=data, proxies=self.proxy, timeout=5)
        result = json.loads(resp.text.replace(f'{data["cb"]}(', '').replace(')', ''))
        if result[0] == 200:
            random_time = random.randint(4414, 4650)
            self.random_time = f'__{result[1] + random_time + 72000000}__{result[1] + random_time}'
            self.wm_tid = result[2]
            self.wm_did = result[3] + self.random_time
            self.wm_ni = result[5]
        else:
            raise Exception('协议更新, 需要重新破解! ')

    def bind_wm_did(self, d):
        """
        客户端与易盾服务器通信, 将该站点与该 wm_did 绑定(d 参数中包含了该站点的 id), 之后的验证请求该站点均可使用该 wm_did
        若无这一步绑定, 需要请求第二次才可以通过
        易盾自家产品无需绑定
        :param d
        :return:
        """
        # url = f"https://{self.host}/v3/b"
        url = "https://webzjac.reg.163.com/v3/b"    # 特殊站点需替换host
        self.session.headers = {
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate',
            'Content-type': 'application/x-www-form-urlencoded',
            'Host': urlparse(url).netloc,
            'Referer': self.local_referer,
            'User-Agent': self.ua
        }
        resp = self.session.post(url=url, data=d["post_data"], proxies=self.proxy, timeout=5)
        result = json.loads(resp.text.replace(f'{d["post_data"]["cb"]}(', '').replace(')', ''))
        if result[0] == 200 and result[2] == self.wm_tid:
            return True
        return False

    def get_config(self):
        """
        获取产品配置
        :return:
        """
        # url = f'{self.protocol}://{self.host}/v2/config/js'
        url = f'{self.protocol}://webzjac.reg.163.com/v2/config/js'     # 特殊站点需替换host
        params = {
            'pn': self.pn,
            'cvk': '',
            'cb': f'__wmjsonp_{B()}',
            't': int(time.time() * 1000)
        }
        self.session.headers = {
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate',
            'Referer': self.local_referer,
            'User-Agent': self.ua
        }
        resp = self.session.get(url, params=params, proxies=self.proxy, timeout=5)
        result = json.loads(resp.text.replace(f'{params["cb"]}(', '').replace(')', ''))
        if result['code'] == 200:
            self.v = result['result']['v']
            self.luv = result['result']['luv']
            self.conf = result['result']['conf']

            # 处理动态 watchman
            self.process_watchman_js()
        else:
            raise Exception('协议更新, 需要重新破解! ')

    def _get_conf(self):
        """
        获取产品编码
        :return:
        """
        url = f'{self.protocol}://{self.host}/api/v2/getconf'
        params = {
            "referer": self.referer,
            "zoneId": "",
            'id': self.sid,
            "ipv6": "false",
            "runEnv": "10",
            "type": "2",
            "loadVersion": "2.2.3",
            'callback': f'__JSONP_{C()}_0'
        }
        self.session.headers = {
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate',
            'Host': urlparse(url).netloc,
            'Referer': self.local_referer,
            'User-Agent': self.ua
        }
        resp = self.session.get(url, params=params, proxies=self.proxy, timeout=5)
        result = json.loads(resp.text.replace(f'{params["callback"]}(', '').replace(');', ''))
        if result['data']['ac']['enable'] == 1:
            self.initWatchman = True
            self.pn = result['data']['ac']['pn']
            self.zoneId = result["data"]["zoneId"]

    def _init_captcha(self):
        """
        初始化验证码
        :return:
        """
        url = f'{self.protocol}://{self.host}/api/v3/get'
        params = {
            "referer": self.referer,
            "zoneId": self.zoneId,
            "acToken": self.ac_token,
            "id": self.sid,
            "fp": self.fp,
            "https": "true",
            "type": "undefined",
            "version": "2.21.1",
            "dpr": "1",
            "dev": "1",
            "cb": core_ctx.call('get_cb')[:64],
            "ipv6": "false",
            "runEnv": "10",
            "group": "",
            "scene": "",
            "lang": "zh-CN",
            "sdkVersion": "undefined",
            "width": self.width,
            "audio": "false",
            "token": self.token,
            "callback": f'__JSONP_{C()}_{self.api_count}'
        }
        self.api_count += 1
        self.session.headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Host': urlparse(url).netloc,
            'Referer': self.local_referer,
            'User-Agent': self.ua
        }
        resp = self.session.get(url, params=params, proxies=self.proxy, timeout=5)
        result = json.loads(resp.text.replace(f'{params["callback"]}(', '').replace(');', ''))
        if not result['error']:
            return result
        return None

    def _captcha_verify(self, data):
        """
        验证
        :param data:
        :return:
        """
        check_url = f'{self.protocol}://{self.host}/api/v3/check'
        params = {
            'referer': self.referer.split('?')[0],
            'zoneId': self.zoneId,
            'id': self.sid,
            'token': self.token,
            'acToken': "undefined",
            'data': data,
            'width': self.width,
            'type': self.type,
            'version': '2.21.1',
            'cb': core_ctx.call('get_cb')[:64],
            'extraData': "",    # ''.join([str(random.randint(1, 10)) for _ in range(7)]) + "@163.com",
            "bf": "0",
            'runEnv': 10,
            "sdkVersion": "undefined",
            'callback': f'__JSONP_{C()}_{self.api_count}'
        }
        self.api_count += 1
        self.session.headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Host': urlparse(check_url).netloc,
            'Referer': self.local_referer,
            'User-Agent': self.ua
        }
        resp = self.session.get(check_url, params=params, proxies=self.proxy, timeout=5)
        result = json.loads(resp.text.replace(f'{params["callback"]}(', '').replace(');', ''))
        if result['data']['result']:
            return {
                'token': result['data']['token'],
                'validate': result['data']['validate']
            }
        return [result['data']['token']]

    def crack(self, is_first=True):
        """
        验证流程
        :return:
        """
        if is_first:
            self._get_conf()

            if self.initWatchman:
                self.get_config()
                logger.debug(f'易盾 -> watchman 版本: {self.v}')
                self.get_wm_did()

        if self.initWatchman:
            ac_data = watchman_ctx.call(
                'acTokenCheck',
                self.protocol, self.pn, self.v, self.luv, self.conf,
                self.sid, self.wm_tid, self.wm_did, self.wm_ni)
            time.sleep(random.randint(1, 3))    # 高并发需延时
            ac_data["d"]["post_data"] = str_to_dict(ac_data['d']["post_data"])
            self.ac_token = ac_data['acToken']
            # wm_nike 目前不知道作用, 不清楚后续是否会校验, 不过在请求目标站点的其他接口 cookie 中有看见, 不知道是不是必需 cookie
            self.wm_nike = ac_data['wm_nike']
            # 有这一步请求才可以一次通过, 否则需要第二次才可以通过；高并发需绑定两次
            if not self.bind_wm_did(ac_data["d"]):
                raise Exception('wm_did 绑定失败! ')

        init_data = self._init_captcha()
        if not init_data:
            raise Exception('验证码初始化失败! ')
        self.type = init_data['data']['type']
        self.xtype = captcha_type.get(str(self.type))
        self.token = init_data['data']['token']
        verify_data = None
        # 加密轨迹
        if self.type == 2:
            logger.debug(f'易盾 -> 触发{self.xtype}验证! ')
            bg = init_data['data']['bg']
            front = init_data['data']['front']
            distance, img_width = _get_distance(front[0], bg[0], self.proxy)
            distance = int(distance * (self.width / img_width))
            verify_data = core_ctx.call('sliderEncrypt', self.token, distance, self.width)

        elif self.type == 3:
            logger.debug(f'易盾 -> 触发{self.xtype}! ')
            bg = init_data['data']['bg'][0]
            captcha = _pic_download(bg, self.proxy)
            data = {'img': base64.b64encode(captcha).decode(), 'front': init_data['data']['front']}
            word = init_data['data']['front']
            result = requests.post(dxtubiao_api, data=json.dumps(data), timeout=20).json()
            points = [result['data'].get(i) for i in list(word)]
            verify_data = core_ctx.call('clickEncrypt', self.token, points)

        elif init_data['data']['type'] == 5:
            logger.debug(f'易盾 -> 触发{self.xtype}! ')
            start_points = {'x': random.randint(300, 370), 'y': random.randint(717, 780)}
            verify_data = core_ctx.call('senseEncrypt', self.token, start_points)

        elif init_data['data']['type'] == 7:
            logger.debug(f'易盾 -> 触发{self.xtype}! ')
            bg = init_data['data']['bg'][0]
            captcha_content = _pic_download(bg, self.proxy)
            data = {'img': captcha_content}
            result = requests.post(dxtubiao_api, data=json.dumps(data), timeout=20).json()
            points = [{"x": int(i[0]), "y": int(i[1])} for i in result['data']]
            verify_data = core_ctx.call('clickEncrypt', self.token, points)

        # 最终验证
        result = self._captcha_verify(verify_data)
        return result

    def run(self):
        flag = True

        # 请求前置页面初始化环境
        self.req_referer()
        for _ in range(3):
            self.proxy = get_proxies()
            self.fp = fingerprint_ctx.call('getFingerprint', self.referer.split('/')[2])
            result = self.crack(flag)
            if isinstance(result, dict):
                logger.info(f'易盾 -> 校验结果: {result}')
                return {
                    'success': 1,
                    'message': f'触发{self.xtype}验证, 校验通过! ',
                    'data': {
                        'token': result['token'],
                        'ip': self.proxy,
                        'validate': core_ctx.call('encryptValidate', result['validate'], self.fp)
                    }
                }
            self.token = result[0]
            flag = False

        return {
            'success': 0,
            'message': f'触发{self.xtype}验证, 未知错误! ',
            'data': None
        }


def test():
    referer = 'https://dl.reg.163.com/webzj/v1.0.1/pub/index_dl2_new.html'
    host = "webzjcaptcha.reg.163.com"
    x = YidunCracker(
        '163',
        '1e48b2e565768181288e9a59d7b933a0', 310,
        referer,
        host
    ).run()
    # print(x)


if __name__ == '__main__':
    from CrawlersTools.schedules import AutoThread

    test()
    # fun_list = [test for _ in range(300)]
    # a_thread = AutoThread(15, fun_list)
    # a_thread.main_thread()
