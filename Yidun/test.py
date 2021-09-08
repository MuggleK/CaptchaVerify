# -*- coding: utf-8 -*-
from urllib.parse import quote, urlencode
from spider_tools import Thread_Grab
import requests
import time
from loguru import logger


# n = 0
# total = 0
# data = {'sid':'9512a1ccb5c148fe8dbccaf8a71b5293','width':320,'referer':"https://register.ccopyright.com.cn/publicInquiry.html"}
# while True:
#     startTime = time.time()
#     total += 1
#     url = 'http://127.0.0.1:7123/yidun?'+ urlencode(data)
#     try:
#         resp = requests.get(url)
#         logger.success(resp.json())
#         if resp.json().get('result').get('data').get('validate'):
#             n += 1
#             logger.debug(f'Total Cost Time：{time.time() - startTime}s', )
#     except:
#         pass
#     logger.debug(f'ACC：{float(n/total)} 当前测试次数：{total}  成功次数：{n}')

# 18

def sss(i):
    url = 'http://127.0.0.1:7123/yidun?sid=a7bef55d9fed4e36a1004f2f8926a617&width=320&referer=https://register.ccopyright.com.cn/login.html'
    resp = requests.get(url, timeout=120)
    print(resp.json())
    print('第{}次测试'.format(i + 1))
    i['pbar'].updated()
#
#
# sss(0)
i = [{'times':i} for i in range(1000)]
Thread_Grab(sss,i,40)
# x = requests.post(
#         'http://47.98.237.27:8778/api/CaptchaServer.php?pname=yidun&token=eYxJ54oFH__U4ysfDzxuZ_79AfRv9Kf_DlED',
#         data={
#             'sid': 'c2e691560a1b4e76b71fd37eed97f46a',
#             'width': 320,
#             'type': 3,
#             'referer': "http://jzsc.mohurd.gov.cn/data/company?complexname"
#         }
#     ).json()
# print(x)
