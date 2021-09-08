# -*- coding: utf-8 -*-

import re
import random
import requests
import json
import time
import math
import execjs
import traceback
import base64
from PIL import Image
from db import RedisClient
from utils import format_print
import os
import uuid
import _locale
from spider_tools import get_ip
from img_locate import _get_distance, _pic_download, get_pos1
import warnings
warnings.filterwarnings("ignore")

_locale._getdefaultlocale = (lambda *args: ['zh_CN', 'utf8'])

dxtubiao_api = 'http://127.0.0.1:5875/captcha'


class YidunCracker:

    def __init__(self, site, sid, width, referer="http://jzsc.mohurd.gov.cn/home"):
        # 调用站点
        self.site = site
        # 调用站点的 id
        self.sid = sid
        # 固定校验类型
        self.type = None
        # 验证码的前置页面, 很重要, 严格站点校验该参数
        self.referer = referer
        self.token = ""
        # 验证码图片在浏览器上的宽
        self.width = int(width)

        # 轨迹点击行为加密
        with open('./static/core.js', 'rb') as f:
            self.core_js = f.read().decode()
        # 加载浏览器环境
        with open('./static/dom.js', 'rb') as f:
            self.dom_js = f.read().decode()
        # 浏览器指纹
        with open('./static/fingerprint.js', 'rb') as f:
            self.fingerprint_js = f.read().decode()
        # acToken 全局加密函数
        with open('./static/watchman.js', 'rb') as f:
            self.encrypt_js = f.read().decode()
        # 工具函数
        with open('./static/tool.js', 'rb') as f:
            self.tool_js = f.read().decode()

        self.core_ctx = execjs.compile(self.core_js)
        self.fingerprint_ctx = execjs.compile(self.dom_js + self.fingerprint_js)
        self.tool_ctx = execjs.compile(self.tool_js)

        # watchman js 函数执行名称
        self.watchman_js = None
        self.watchman_ctx = None

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

        # wm_did 缓存
        self.wm_config = {}
        self.localStorage = None

        # 协议域名解析
        self.protocol = self.referer.split('://')[0]
        self.host = self.referer.split('/')[2]

        # 指纹缓存
        self._localStorage = RedisClient('dun163_fingerprint', '2.13.6')
        format_print('易盾', '开始读取指纹...')
        self.fp_config = self._localStorage.get(self.site)
        if not self.fp_config:
            format_print('易盾', '该站点无指纹, 获取中...')
            self.fp = self.fingerprint_ctx.call('getFingerprint', self.host)
            # print(self.fp)
            self.fp_config = json.dumps({
                'fp': self.fp,
                'expireTime': self.fp.split(':')[1]
            })
            self._localStorage.set(self.site, self.fp_config)
            # 设置 15s 有效期
            self._localStorage.expire(15)
            format_print('易盾', '指纹获取完成, 已存入数据库! ')
        else:
            self.fp_config = json.loads(self.fp_config)
            if int(self.fp_config['expireTime']) < int(time.time() * 1000) - 60:
                format_print('易盾', '该站点指纹已过期, 重新获取中...')
                self.fp = self.fingerprint_ctx.call('getFingerprint', self.host)
                self.fp_config = json.dumps({
                    'fp': self.fp,
                    'expireTime': self.fp.split(':')[1]
                })
                self._localStorage.set(self.site, self.fp_config)
                # 设置 15s 有效期
                self._localStorage.expire(15)
                format_print('易盾', '指纹获取完成, 已存入数据库! ')
            else:
                self.fp = self.fp_config['fp']
                format_print('易盾', '指纹读取完成: {}'.format(self.fp))

        self.session = requests.session()

        # 这两个域名都可以用
        self.server = ['c.dun.163yun.com', 'webzjcaptcha.reg.163.com']

        self.api_count = 0
        self.proxy = None

    def read_cache(self):
        """
        读取 redis 缓存
        :return:
        """
        format_print('易盾', '开始读取 wm_did 缓存配置...')
        # 用于随机取 wm_did, 因为不确定同一个 wm_did 大量使用是否会缩短使用期, 如果大量跑可以选择随机取
        # 或者专门写一个脚本用于生产 wm_did
        # self.wm_config = self.localStorage.random()
        # 取该网站的 wm_did
        self.wm_config = self.localStorage.get(self.site)

        if not self.wm_config:
            format_print('易盾', '该站点无缓存, 协议获取中...')
            self.get_wm_did()
            self.wm_config = {
                'pn': self.pn,
                'v': self.v,
                'luv': self.luv,
                'conf': self.conf,
                'wm_tid': self.wm_tid,
                'wm_did': self.wm_did,
                'wm_ni': self.wm_ni
            }
            self.localStorage.set(self.site, json.dumps(self.wm_config))
            # 每个 wm_did 有 20 个小时的有效期, 设置过期时间: 18 小时     高并发下wm_did有效时长20S
            self.localStorage.expire(15)
            format_print('易盾', '该站点 wm_did 配置已存入数据库! ')
        else:
            self.wm_config = json.loads(self.wm_config)
            self.pn = self.wm_config['pn']
            self.v = self.wm_config['v']
            self.luv = self.wm_config['luv']
            self.conf = self.wm_config['conf']
            self.wm_tid = self.wm_config['wm_tid']
            self.wm_did = self.wm_config['wm_did']
            self.wm_ni = self.wm_config['wm_ni']
            format_print('易盾', 'wm_did 缓存读取完成: {}'.format(self.wm_config))

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
            'Host': self.host,
            'Referer': f'{self.protocol}://{self.host}/home',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
        }
        self.session.get(self.referer, proxies=self.proxy, timeout=5)

    def process_watchman_js(self):
        """
        处理 watchman js  版本更新需对应特定版本改写
        :return:
        """
        # self.v = '2.6.2_c2bb0782'
        self.v = '2.7.3_eb045ea7'
        watchman_js_url = f'{self.protocol}://acstatic-dun.126.net/{self.v}/watchman.min.js'
        self.session.headers = {
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'acstatic-dun.126.net',
            'Referer': self.referer,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
        }
        watchman_js = self.session.get(watchman_js_url, timeout=5).text

        funcs = re.findall(r'prototype.(.*?),void 0\)\(..concat', watchman_js, re.S)[0].split('prototype.')

        # 延时函数名
        delay_func_name = funcs[-2].split('=')[0]

        # d 接口 d 参数对象生成函数名
        dd_func_name = funcs[-1].split('=')[0]
        # d 接口 d 参数变量名
        variable1 = funcs[-1].split('[0];')[-1].split('=')[0]

        # b 接口 d 参数对象生成函数名
        bd_func_name = re.findall(r'_stop\(\)};.*prototype.(.*?)=.*?console\.log', watchman_js, re.S)[0]
        _bd_func = re.findall(f'prototype.{bd_func_name}(.*?)prototype', watchman_js, re.S)[0]
        # b 接口 d 参数变量名
        # variable2 = _bd_func.split('[0];')[-1].split('=')[0]
        variable2 = _bd_func.split('[0];')[-2].split('=')[0]

        # 处理延时函数
        delay_func = re.findall(f'prototype.{delay_func_name}(.*?)prototype', watchman_js, re.S)[0]
        delay_func = re.findall('{(.*?)};', delay_func, re.S)[0]
        watchman_js = watchman_js.replace(delay_func, '')

        # 处理 d 接口 d 参数对象生成函数
        dd_func = re.findall(f'prototype.{dd_func_name}=.*?prototype', watchman_js, re.S)[0]
        __dd_func = re.findall(r'.\..\(.*?\)', dd_func)[0]
        ___dd_func = __dd_func.replace(f',{variable1},', ',window.d1,')
        _dd_func = re.sub(f'];{variable1}=', '];window.d1=', dd_func)
        _dd_func = _dd_func.replace(__dd_func, ___dd_func)
        watchman_js = watchman_js.replace(dd_func, _dd_func)

        # 处理 b 接口 d 参数对象生成函数
        bd_func = re.findall(f'prototype.{bd_func_name}.*?prototype', watchman_js, re.S)[0]
        _bd_func = re.sub(f'{variable2},function', 'window.d2,function', bd_func)
        _bd_func = re.sub(f'];{variable2}=', '];window.d2=', _bd_func)
        __bd_func = ',' + _bd_func.split('1,')[1].split(';')[0]
        _bd_func = _bd_func.replace(__bd_func, '')
        watchman_js = watchman_js.replace(bd_func, _bd_func)
        # print(watchman_js)

        # 处理延时变量
        assign_func = re.findall(r'function .{2}\(.{1},.{1}\).*hasOwnProperty',watchman_js)[0].split('function')[1].split('(')[0].strip()
        variable3 = re.findall(r'(%s\({.*?},..:.*?,)' % assign_func, watchman_js)[0]
        variable3_ = variable3.split(':')[-1]
        variable3_ = variable3.replace(variable3_, '!1,')
        watchman_js = watchman_js.replace(variable3, variable3_)
        # print(watchman_js)

        # 处理计时变量    Fc暂时写死
        ec = re.findall(r'\.Fc=.\(\)-.', watchman_js)[0]
        if self.type in {3, 7, 9}:
            _ec = '+random(13260, 13800)'
        else:
            _ec = '+random(1326, 1380)'
        watchman_js = watchman_js.replace(ec, ec + _ec)
        # 处理 ia
        d = re.findall(r'=(.).merged;', watchman_js)[0]
        watchman_js = watchman_js.replace('.merged;', f'.merged,ia={d}.ia;')
        watchman_js = watchman_js.replace('auto:', 'ia:ia,auto:')

        # 处理计时变量    Fc暂时写死
        ec = re.findall(r'\.Fc=.\(\)-.', watchman_js)[0]
        if self.type in {3, 7, 9}:
            _ec = '+random(13260, 13800)'
        else:
            _ec = '+random(1326, 1380)'
        watchman_js = watchman_js.replace(ec, ec + _ec)

        # 处理 watchman 初始化时长 $写死
        v0 = re.findall(r'return.*?\$\[0]', watchman_js)[0].split('return ')[-1]
        watchman_js = watchman_js.replace(v0, f'{random.randint(5, 12)}')
        # 识别时间
        v1 = re.findall(r'return.*?\$\.slice.*?\)', watchman_js)[0].split('return ')[-1]
        watchman_js = watchman_js.replace(v1,
                                          f"[{random.randint(0, 10)}, {random.randint(0, 10)}, {random.randint(0, 5)}, {random.randint(500, 1000)}, {random.randint(0, 5)}]")

        # 处理轨迹时间    za S写死
        ua = re.findall(r'(\.za=.);', watchman_js)[0]
        watchman_js = watchman_js.replace(ua, ua + '-100')
        i = re.findall(r'].S(.*?)switch', watchman_js)[0]
        j = i.replace('()', '()+random(1000,2000)')
        self.watchman_js = watchman_js.replace(i, j)

    def get_wm_did(self):
        """
        协议获取 wm_did
        :return:
        """
        url = f'{self.protocol}://ac.dun.163yun.com/v3/d'
        d = self.watchman_ctx.call('get_dd', self.protocol, self.pn, self.v, self.luv, self.conf)
        data = {
            'd': d,
            'v': self.v.split('_')[1],
            'cb': '_WM_'
        }
        self.session.headers = {
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate',
            'Content-type': 'application/x-www-form-urlencoded',
            'Origin': self.referer.split('?')[0],
            'Host': 'ac.dun.163yun.com',
            'Referer': self.referer.split('?')[0],
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
        }
        resp = self.session.post(url, data=data, proxies=self.proxy, timeout=5)
        result = json.loads(resp.text.replace('_WM_(', '').replace(')', ''))
        format_print('易盾', 'wm_did 请求结果: {}'.format(result))
        if result[0] == 200:
            random_time = random.randint(4414,4650)
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
        url = f'{self.protocol}://ac.dun.163yun.com/v3/b'

        data = {
            'd': d,
            'v': self.v.split('_')[1],
            'cb': '_WM_'
        }
        self.session.headers = {
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate',
            'Content-type': 'application/x-www-form-urlencoded',
            'Origin': self.referer.split('?')[0],
            'Host': 'ac.dun.163yun.com',
            'Referer': self.referer.split('?')[0],
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
        }
        resp = self.session.post(url, data=data, proxies=self.proxy, timeout=5)
        result = json.loads(resp.text.replace('_WM_(', '').replace(')', ''))
        if result[0] == 200 and result[2] == self.wm_tid:
            return True
        return False

    def get_config(self):
        """
        获取产品配置
        :return:
        """
        url = f'{self.protocol}://webzjac.reg.163.com/v2/config/js'
        params = {
            'pn': self.pn,
            'cb': f'__wmjsonp_{self.tool_ctx.call("B")}',
            't': int(time.time() * 1000)
        }
        self.session.headers = {
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate',
            'Referer': self.referer,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
        }
        resp = self.session.get(url, params=params, proxies=self.proxy, timeout=5)
        result = json.loads(resp.text.replace(f'{params["cb"]}(', '').replace(')', ''))
        # print(result)
        if result['code'] == 200:
            self.v = result['result']['v']

            self.luv = result['result']['luv']
            self.conf = result['result']['conf']

            self.localStorage = RedisClient('dun163_wm_did', self.v)
            # 处理动态 watchman
            self.process_watchman_js()
            # print(self.dom_js + self.watchman_js + self.encrypt_js)
            self.watchman_ctx = execjs.compile(self.dom_js + self.watchman_js + self.encrypt_js)
        else:
            raise Exception('协议更新, 需要重新破解! ')

    def _get_conf(self):
        """
        获取产品编码
        :return:
        """
        url = f'{self.protocol}://c.dun.163yun.com/api/v2/getconf'
        params = {
            'id': self.sid,
            'ipv6': False,
            'runEnv': 10,
            'referer': self.referer.split('?')[0],
            'callback': f'__JSONP_{self.tool_ctx.call("C")}_0'
        }
        self.session.headers = {
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'c.dun.163yun.com',
            'Referer': self.referer,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
        }
        resp = self.session.get(url, params=params, proxies=self.proxy, timeout=5)
        result = json.loads(resp.text.replace(f'{params["callback"]}(', '').replace(');', ''))
        try:
            if result['data']['ac']['enable'] == 1:
                self.initWatchman = True
                self.pn = result['data']['ac']['pn']
        except:
            traceback.print_exc()

    def _init_captcha(self):
        """
        初始化验证码
        :return:
        """
        url = f'{self.protocol}://c.dun.163yun.com/api/v2/get'
        params = {
            'id': self.sid,
            'fp': self.fp,
            'https': True if self.protocol == "https" else False,
            'type': self.type,
            'version': '2.13.6',
            'dpr': '1',
            'dev': '1',
            'group': '',
            'scene': '',
            'cb': self.core_ctx.call('get_cb')[:64],
            'ipv6': False,
            'runEnv': 10,
            'width': self.width,
            'token': self.token,
            'referer': self.referer.split('?')[0],
            'callback': f'__JSONP_{self.tool_ctx.call("C")}_{self.api_count}'
        }
        self.api_count += 1
        self.session.headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Host': 'c.dun.163yun.com',
            'Referer': self.referer,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
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
        check_url = f'{self.protocol}://c.dun.163yun.com/api/v2/check'
        params = {
            'id': self.sid,
            'token': self.token,
            'acToken': self.ac_token,
            'data': data,
            'width': self.width,
            'type': self.type,
            'version': '2.13.6',
            'cb': self.core_ctx.call('get_cb')[:64],
            'extraData': '',
            'runEnv': 10,
            'referer': self.referer.split('?')[0],
            'callback': f'__JSONP_{self.tool_ctx.call("C")}_{self.api_count}'
        }
        self.api_count += 1
        self.session.headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Host': 'c.dun.163yun.com',
            'Referer': self.referer,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
        }
        resp = self.session.get(check_url, params=params, proxies=self.proxy, timeout=5)
        result = json.loads(resp.text.replace(f'{params["callback"]}(', '').replace(');', ''))
        format_print('易盾', '校验结果: {}'.format(result))
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
                format_print('易盾', f'watchman 版本: {self.v}')
                self.read_cache()

        init_data = self._init_captcha()
        self.type = init_data['data']['type']
        if not init_data:
            raise Exception('验证码初始化失败! ')

        self.token = init_data['data']['token']

        if init_data['data']['type'] == 2:
            format_print('易盾', '触发滑块验证! ')
            xtype = '滑块'
            bg = init_data['data']['bg']
            front = init_data['data']['front']
            distance, img_width = _get_distance(front[0], bg[0], self.proxy)
            distance = int(distance * (self.width / img_width))
            format_print('cv2 模板匹配', '缺口距离: {}'.format(distance))
            # time.sleep(random.randint(3,10))
            data = self.core_ctx.call('sliderEncrypt', self.token, distance, self.width)

        elif init_data['data']['type'] == 5:
            format_print('易盾', '触发无感! ')
            xtype = '无感'
            start_points = {'x': random.randint(300, 370), 'y': random.randint(717, 780)}
            # points = [start_points,{'x':start_points['x'] + 15,'y':start_points['y'] + 2}]
            points = [{'x': 367, 'y': 721}, {'x': 370, 'y': 760}]
            data = self.core_ctx.call('senseEncrypt', self.token, points)
            # print('轨迹data :', data)

        elif init_data['data']['type'] == 7:
            xtype = "图标点选"
            bg = init_data['data']['bg'][0]
            captcha = _pic_download(bg, "icon", self.proxy)
            Image.open(captcha).resize((320, 240)).save(captcha)
            with open(captcha, 'rb') as f:
                s = base64.b64encode(f.read())
                data = {'img': s.decode()}
            # data = {'image': f.read()}
            # data = f.read()
            result = requests.post(dxtubiao_api, data=json.dumps(data),
                                   timeout=20).json()
            # result = requests.post(dxtubiao_api, files=data,timeout=40).json()
            if result:
                points = [{"x": int(i[0]), "y": int(i[1])} for i in result['data']]
                # points = result['data']
                data = self.core_ctx.call('clickEncrypt', self.token, points)
                mouse_end = points[0]

        elif init_data['data']['type'] == 3:
            format_print('易盾', '触发文字点选! ')
            xtype = "文字点选"
            bg = init_data['data']['bg'][0]
            captcha = _pic_download(bg, "icon", self.proxy)
            Image.open(captcha).resize((320, 160)).save(captcha)
            with open(captcha, 'rb') as f:
                s = base64.b64encode(f.read())
                data = {'img': s.decode(), 'front': init_data['data']['front']}

            # data = f.read()
            word = init_data['data']['front']
            result = requests.post(dxtubiao_api, data=json.dumps(data),
                                   timeout=20).json()
            points = result['data']
            data = self.core_ctx.call('clickEncrypt', self.token, points)
            mouse_end = points[0]

        if self.initWatchman:
            # print(','.join([self.protocol, self.pn, self.v, self.luv, self.conf,
            #       self.sid, self.wm_tid, self.wm_did, self.wm_ni]))
            ac_data = self.watchman_ctx.call(
                'acTokenCheck',
                self.protocol, self.pn, self.v, self.luv, self.conf,
                self.sid, self.wm_tid, self.wm_did, self.wm_ni)
            d = ac_data['d']
            self.ac_token = ac_data['acToken']
            # wm_nike 目前不知道作用, 不清楚后续是否会校验, 不过在请求目标站点的其他接口 cookie 中有看见, 不知道是不是必需 cookie
            self.wm_nike = ac_data['wm_nike']
            # 有这一步请求才可以一次通过, 否则需要第二次才可以通过
            if not self.bind_wm_did(d):
                raise Exception('wm_did 绑定失败! ')

        # 最终验证
        result = self._captcha_verify(data)
        return xtype, result

    def run(self):
        flag = True
        num = 0

        # 请求前置页面初始化环境
        self.req_referer()
        while True:
            xtype, result = self.crack(flag)
            if isinstance(result, dict):
                return {
                    'success': 1,
                    'message': f'触发{xtype}验证, 校验通过! ',
                    'data': {
                        'token': result['token'],
                        'ip': self.proxy,
                        'validate': self.core_ctx.call('encryptValidate', result['validate'], self.fp)
                    }
                }
            # 控制重试次数, 一般两次内不通过即放弃
            elif num >= 2:
                if self.initWatchman:
                    # wm_did 失效, 删除
                    self.localStorage.delete(self.site)
                if isinstance(result, str):
                    return {
                        'success': 0,
                        'message': f'触发{xtype}验证, {result}' if xtype else result,
                        'data': None
                    }
                elif isinstance(result, list):
                    return {
                        'success': 1,
                        'message': f'触发{xtype}验证, 校验失败! ',
                        'data': {
                            'token': result[0],
                            'validate': None
                        }
                    }
                else:
                    return {
                        'success': 0,
                        'message': f'触发{xtype}验证, 未知错误! ',
                        'data': None
                    }

            self.token = result[0]
            flag = False
            num += 1
            # break


if __name__ == '__main__':
    referer = 'https://etax.jiangsu.chinatax.gov.cn/portal/queryapi/commonPage.do'
    # while True:
    x = YidunCracker(
        '163',
        '1a623022803d4cbc86fa157ec267bb36', 320,
        referer
    ).run()
    print(x)

    url = 'https://etax.jiangsu.chinatax.gov.cn/portal/queryapi/query.do'
    data = {
        'request': json.dumps({"action":"query_ggcx_Ajxynsrcx","body":{"nsrsbh":"91320205752040267Y","pdnd":"2021","nevalidate":f"CN31_{x.get('data').get('validate')}","datagrid":"","configid":"query_ggcx_Ajxynsrcx","tycx":"3","tj0":"NSRSBH","tj1":"NSRSBH","tj2":"NSRSBH","tj3":"2021","tj4":"NSRSBH","tj5":"NSRSBH","tj6":"2021"}})
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
    }
    res = requests.post(url=url,data=data,headers=headers)
    print(res.status_code)
    print(res.json())
    # time.sleep(3)
    # except Exception as e:
    #     print(e)
