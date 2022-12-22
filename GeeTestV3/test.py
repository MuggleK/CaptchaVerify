import requests, time, json, re
from urllib.parse import quote
from loguru import logger
import warnings

import vthread

warnings.filterwarnings('ignore')


def get_ip(proxy_type="random"):
    """
    qzd_proxy：亿牛云+星速云
    @param proxy_type: 默认取随机
    @return:
    """
    try:
        proxy = requests.get(f"http://192.168.9.3:55555/{proxy_type.lower()}").text.strip()
        return {'http': 'http://' + proxy, 'https': 'http://' + proxy}
    except Exception as err:
        logger.error(f'获取代理失败：{err}')


def get_validate_wander(challenge, gt):
    proxy = None
    # # url = "http://112.126.79.215:5685/captcha"
    url = "http://175.178.127.140:5685/captcha"
    data = {'gt': gt, 'challenge': challenge, 'proxy': proxy}
    response = requests.get(url=url, params=data)
    return response.json()
    # from main import CaptValidate
    # geetest = CaptValidate()
    # res = geetest.run(gt, challenge, None)
    # return res


def run():
    # while True:
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'
        }
        session = requests.session()
        # query_url = f'https://www.geetest.com/demo/gt/register-click-official?t={int(time.time() * 1000)}'
        session.get('http://qyxy.scjgj.beijing.gov.cn/home',headers=headers,proxies=None,timeout=60)

        query_url = f'http://qyxy.scjgj.beijing.gov.cn/server-api/gt/register?t={int(time.time() * 1000)}'

        # query_url = f'https://www.geetest.com/demo/gt/register-icon?t={int(time.time() * 1000)}'
        # query_url = f'https://525scw.com/api/v1/account/webapi/account/userss/startCaptcha'

        query_res = session.get(url=query_url, headers=headers, proxies=None).json()
        print(query_res)
        gt = query_res['gt']
        challenge = query_res['challenge']
        s = get_validate_wander(challenge, gt)
        print(s)
        time.sleep(3)
    except Exception as e:
        print(e)


def zd_demo():
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
    gt = re.findall('"gt":"(.*?)"', query_res)[0]
    challenge = re.findall('"challenge":"(.*?)"', query_res)[0]

    result = get_validate_wander(challenge, gt)
    challenge_ = result.get('data').get('challenge')
    validate_ = result.get('data').get('validate')

    url = f'https://ss.cods.org.cn/latest/searchR?q={quote(quote(query_word))}&t=common&currentPage=1&searchToken=&geetest_challenge={challenge_}&geetest_validate={validate_}&geetest_seccode={validate_}|jordan'
    res = session.get(url=url, headers=headers, proxies=proxy).text
    print(res)


@vthread.pool(30)
def geest_demo(i):
    """ 极验官网demo """

    session = requests.session()
    url = 'https://www.qybz.org.cn/gc/geetest/login?t={}'.format(int(time.time() * 1000))
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}

    res = session.get(url, headers=headers).json()
    gt = re.findall('"gt":"(.*?)"', res)[0]
    challenge = re.findall('"challenge":"(.*?)"', res)[0]
    result = get_validate_wander(challenge, gt)
    logger.info(result)

    # search_url = f'https://www.qybz.org.cn/user/searchR?keyword=xiaomi&pageNo=1&standardType=&standardStatus=&xzqh=&geetest_challenge={result["data"]["challenge"]}&geetest_validate={result["data"]["validate"]}&geetest_seccode={result["data"]["validate"]}|jordan'
    # search_res = session.get(url=search_url, headers=headers)
    # print(search_res.text)


if __name__ == '__main__':
    # while True:
    # geest_demo(1)
    for i in range(100000):
        geest_demo(i)
