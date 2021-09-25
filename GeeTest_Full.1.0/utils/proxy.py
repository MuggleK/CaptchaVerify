import requests
import time
import random


def red_print(str):
    print('\033[31m{}\033[0m'.format(str))


def my_request(url, conn=requests, proxy=None, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
               , allow_status=[200], timeout=(10, 20), method='get', data=None, retry=5,
               timesleep=0, show_result=False, allow_redirects=False, verify=False, change_ip_times=5):
    request_count = 0
    status_code_not_allow = 0
    while True:
        if proxy and status_code_not_allow > change_ip_times:
            proxy = get_ip()
        try:
            if method.lower() == 'get':
                response = conn.get(
                    url=url, headers=headers, data=data, timeout=timeout,
                    allow_redirects=allow_redirects,
                    proxies=proxy, verify=verify)
                # print("响应状态：{} 访问url：{}".format(response.status_code, url))
                if response.status_code in allow_status:
                    return {'res': response, 'conn': conn, 'proxy': proxy}
                if response.status_code not in allow_status:
                    status_code_not_allow += 1
                if proxy and response.status_code == 403 or response.status_code == 407:
                    proxy = get_ip()
                if show_result:
                    print(response.text)

            elif method.lower() == 'post':
                response = conn.post(url=url, headers=headers, data=data, timeout=timeout,
                                     allow_redirects=allow_redirects,
                                     proxies=proxy, verify=verify)
                print("响应状态：{} 访问url：{} 请求参数：{}".format(response.status_code, url, data))
                if response.status_code in allow_status:
                    return {'res': response, 'conn': conn, 'proxy': proxy}
                if response.status_code not in allow_status:
                    status_code_not_allow += 1
                if proxy and response.status_code == 403:
                    proxy = get_ip()
                if show_result:
                    print(response.text)
        except:
            print("本次请求失败,重试次数剩余：{}".format(retry - request_count))
            proxy = get_ip()
        request_count += 1
        time.sleep(timesleep)
        if request_count > retry - 1:
            red_print("请求失败 request_way：{} URL：{} data：{} retry_times：{}".format(method, url, data, retry))
            return


def get_ip():
    # return None
    while True:
        try:
            ip = requests.get(url='http://219.151.149.149:8888/get_ips/?user_code=688688&user_key=688688').text.split(
                '\n')
            return {
                'https:': random.choice(ip),
                'http:': random.choice(ip)
            }
        except:
            pass
