# -*- coding: utf-8 -*-
# @Project : Yidun
# @Time    : 2022/12/14 17:29
# @Author  : MuggleK
# @File    : settings.py
import os

from execjs import compile

# 轨迹点击行为加密
with open('./static/core.js', 'rb') as f:
    core_js = f.read().decode()
# 加载浏览器环境
with open('./static/dom.js', 'rb') as f:
    dom_js = f.read().decode()
# 浏览器指纹
with open('./static/fingerprint.js', 'rb') as f:
    fingerprint_js = f.read().decode()
# acToken 全局加密函数
with open('./static/watchman.js', 'rb') as f:
    encrypt_js = f.read().decode()
core_ctx = compile(core_js)
fingerprint_ctx = compile(dom_js + fingerprint_js)

# watchman
is_exists = [k for i, j, k in os.walk('./static') if "source_watchman.js" in k]
if is_exists:
    with open('./static/source_watchman.js', 'rb') as f:
        watchman_js = f.read().decode()
    watchman_ctx = compile(dom_js + watchman_js + encrypt_js)
else:
    watchman_ctx = None


captcha_type = {"2": "滑块", "5": "无感", "7": "图标点选", "3": "文字点选"}

dxtubiao_api = 'http://175.178.127.140:5675/captcha'
