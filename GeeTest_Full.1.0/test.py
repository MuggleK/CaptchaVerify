import requests,time,json,re
from urllib.parse import quote
from multiprocessing.dummy import Pool as ThreadPool

def get_ip():
    return None
    while True:
        try:
            ip = requests.get(url='http://119.3.187.233:8005/ip', timeout=10).json()
            return ip
        except:
            pass


def get_validate_wander(challenge,gt):

    # proxy = get_ip()
    url = "http://127.0.0.1:8044/geetest/verify"
    data = {'gt':gt,'challenge':challenge,'proxy':None}
    response = requests.get(url=url,params=data)
    return response.json()

def run():
    # while True:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'
            }
            session = requests.session()
            query_url = f'http://cx.cnca.cn/CertECloud/geetest/init'
            query_res = session.get(url=query_url, headers=headers).json()
            print(query_res)
            gt = query_res['gt']
            challenge = query_res['challenge']
            s = get_validate_wander(challenge, gt)
            print(s)
        except:
            pass

def Zd_demo():
    """ 组织机构代码demo """

    query_word = '大渡口小学'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'
    }
    proxy = get_ip()
    session = requests.session()
    query_url = f'https://ss.cods.org.cn/gc/geetest/query?t={int(time.time() * 1000)}'
    query_res = session.get(url=query_url, headers=headers, proxies = proxy).text
    query_res = json.loads(query_res)
    gt = re.findall('"gt":"(.*?)",', query_res)[0]
    challenge = re.findall('"challenge":"(.*?)",', query_res)[0]

    result = get_validate_wander(challenge, gt)
    challenge_ = result.get('data').get('challenge')
    validate_ = result.get('data').get('validate')

    url = f'https://ss.cods.org.cn/latest/searchR?q={quote(quote(query_word))}&t=common&currentPage=1&searchToken=&geetest_challenge={challenge_}&geetest_validate={validate_}&geetest_seccode={validate_}|jordan'
    res = session.get(url=url, headers=headers, proxies = proxy).text
    print(res)

if __name__ == '__main__':
    # for i in range(10):
    run()
    # pool = ThreadPool(100)
    # for i in range(100):
    #     pool.apply_async(run)
    # pool.close()
    # pool.join()
