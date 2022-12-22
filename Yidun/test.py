# -*- coding: utf-8 -*-
import requests


def sss():
    url = 'http://127.0.0.1:5000/yidun'
    data = {
        "sid": "1e48b2e565768181288e9a59d7b933a0",
        "width": "340",
        "referer": 'https://dl.reg.163.com/webzj/v1.0.1/pub/index_dl2_new.html',
        "host": "webzjcaptcha.reg.163.com"
    }
    resp = requests.post(url, data=data, timeout=120)
    print(resp.json())


sss()
