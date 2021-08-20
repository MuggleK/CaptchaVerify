# -*- coding: utf-8 -*-
from urllib.parse import quote, urlencode
from spider_tools import Thread_Grab
import requests
import time
from loguru import logger


n = 0
total = 0
data = {'sid':'1a623022803d4cbc86fa157ec267bb36','width':320,'referer':"https://etax.jiangsu.chinatax.gov.cn/portal/queryapi/commonPage.do"}
while True:
    startTime = time.time()
    total += 1
    url = 'http://127.0.0.1:7123/yidun?'+ urlencode(data)
    resp = requests.get(url)
    logger.success(resp.json())
    if resp.json().get('result').get('data').get('validate'):
        n += 1
        logger.debug(f'Total Cost Time：{time.time() - startTime}s', )
    logger.debug(f'ACC：{float(n/total)} 当前测试次数：{total}  成功次数：{n}')


# def sss(i):
#     url = 'http://127.0.0.1:7123?sid=1a623022803d4cbc86fa157ec267bb36&width=320&referer=https://etax.jiangsu.chinatax.gov.cn/portal/queryapi/commonPage.do'
#     resp = requests.get(url, timeout=120)
#     print(resp.json())
#     print('第{}次测试'.format(i + 1))
#
#
# sss(0)
# i = [i for i in range(1000)]
# i.reverse()
# Thread_Grab(sss,i,1)
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
