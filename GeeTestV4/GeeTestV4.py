import requests
import json
import random
import re
import utils.tools as tl
from loguru import logger


class GeeTestV4:

    def __init__(self, captcha_id, risk_type='slide'):
        self.session = None
        self.captcha_id = captcha_id
        self.challenge = tl.uuid()
        self.risk_type = risk_type
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'
        }
        self.aes_key = tl.aeskey()  # 唯一aeskey
        self.aes = tl.AESCipher(self.aes_key)
        with open('./utils/slide.json', 'r', encoding='utf-8') as f:
            self.slide_track = json.loads(f.read())
        self.isDebug = True  # 是否开启调试

    def init(self):
        init_url = 'https://gcaptcha4.geetest.com/load'
        init_params = {
            'captcha_id': self.captcha_id,
            'challenge': self.challenge,
            'client_type': 'web',
            'risk_type': self.risk_type,
            'callback': ''
        }
        init_res = self.session.get(url=init_url, params=init_params, headers=self.headers, timeout=20).text
        init_json = json.loads(re.findall('(?<=\().*(?=\))', init_res)[0])
        if init_json.get('status'):
            if self.isDebug:
                logger.debug(f'init_json -> {init_json}')
            return init_json

    def Ct_process(self, init_json):
        """ 检测gct版本 """
        ct_url = 'https://static.geetest.com' + init_json.get('data').get('gct_path')
        ct_js = self.session.get(url=ct_url, headers=self.headers, timeout=30).text
        fun = re.findall('\[0\];function (.{4})\((.{1})\)(.*?)return function', ct_js)[0]
        fun_1 = 'function ' + fun[0] + f'({fun[1]})' + fun[2].split('function')[0]
        fun_2 = 'function' + 'function'.join(fun[2].split('function')[1:])
        ct_dict = {
            'ct_key': tl.ct_key(ct_js),
            'ct_value': str(tl.Calstr(fun_2 + str(tl.Calstr(fun_1))))
        }
        if self.isDebug:
            logger.success('动态ct：{}'.format(ct_dict))
        return ct_dict

    def img_process(self, init_json):
        bg = 'https://static.geetest.com/' + init_json['data']['bg']
        slice = 'https://static.geetest.com/' + init_json['data']['slice']
        distance, img_width = tl.get_distance(slice, bg, None)
        distance = distance - 15
        if self.isDebug:
            logger.debug(f'Slide Distance -> {distance}')
        return distance

    def verify(self, init_json, ct_dict, slide_distance=0):
        verify_url = 'https://gcaptcha4.geetest.com/verify'
        decrypt_data = {}
        if init_json['data']['captcha_type'] == 'slide':
            if self.slide_track.get(str(slide_distance)):
                slide_list = json.loads(random.choice(self.slide_track[str(slide_distance)]))
            else:
                slide_list = tl.get_track(slide_distance)
            passtime = slide_list[-1][-1]
            decrypt_data = {
                "setLeft": slide_distance,
                "track": slide_list,
                "passtime": passtime,
                "userresponse": slide_distance / 1.0059466666666665,
                "geetest": "captcha",
                "lang": "zh",
                "ep": "123",
                ct_dict['ct_key']: ct_dict['ct_value'],
                "em": {
                    "ph": 0,
                    "cp": 0,
                    "ek": "11",
                    "wd": 1,
                    "nt": 0,
                    "si": 0,
                    "sc": 0
                }
            }
        elif init_json['data']['captcha_type'] == 'match':
            decrypt_data = {
                "passtime": random.randint(200, 1300),
                "userresponse": tl.match_icon(init_json['data']['ques']),
                "geetest": "captcha",
                "lang": "zh",
                "ep": "123",
                ct_dict['ct_key']: ct_dict['ct_value'],
                "em": {
                    "ph": 0,
                    "cp": 0,
                    "ek": "11",
                    "wd": 1,
                    "nt": 0,
                    "si": 0,
                    "sc": 0
                }
            }
        elif init_json['data']['captcha_type'] == 'winlinze':
            decrypt_data = {
                "passtime": random.randint(200, 1300),
                "userresponse": tl.five_points(init_json['data']['ques']),
                "geetest": "captcha",
                "lang": "zh",
                "ep": "123",
                ct_dict['ct_key']: ct_dict['ct_value'],
                "em": {
                    "ph": 0,
                    "cp": 0,
                    "ek": "11",
                    "wd": 1,
                    "nt": 0,
                    "si": 0,
                    "sc": 0
                }
            }
        elif init_json['data']['captcha_type'] == 'pencil':
            pencil_content = self.session.get('https://static.geetest.com/' + init_json['data']['imgs']).content
            pencil_trace = tl.fp_trace(pencil_content)
            decrypt_data = {
                "passtime": random.randint(200, 1300),
                "userresponse": pencil_trace,
                "geetest": "captcha",
                "lang": "zh",
                "ep": "123",
                ct_dict['ct_key']: ct_dict['ct_value'],
                "em": {
                    "ph": 0,
                    "cp": 0,
                    "ek": "11",
                    "wd": 1,
                    "nt": 0,
                    "si": 0,
                    "sc": 0
                }
            }
        aes_encoding = self.aes.new_after_aes(json.dumps(decrypt_data, ensure_ascii=False).replace(' ', ''))
        rsa_encoding = tl.RSA_encrypt(self.aes_key)
        w = aes_encoding + rsa_encoding
        verify_params = {
            'captcha_id': self.captcha_id,
            'challenge': self.challenge,
            'client_type': 'web',
            'lot_number': init_json['data']['lot_number'],
            'risk_type': init_json['data']['captcha_type'],
            'pt': init_json['data']['pt'],
            'w': w,
            'callback': ''
        }
        verify_res = self.session.get(url=verify_url, params=verify_params, headers=self.headers, timeout=20).text.split('(')[1].split(')')[0]
        verify_json = json.loads(verify_res)
        return verify_json

    def main(self):
        self.session = requests.session()
        init_json = self.init()
        ct_dict = self.Ct_process(init_json)
        distance = 0
        if init_json['data']['captcha_type'] == 'slide':
            distance = self.img_process(init_json)
        verify_data = self.verify(init_json, ct_dict, distance)
        if verify_data['data']['result'] == 'success':
            login_url = 'https://gt4.geetest.com/demo/login'
            login_params = {
                'lot_number': verify_data['data']['seccode']['lot_number'],
                'pass_token': verify_data['data']['seccode']['pass_token'],
                'gen_time': verify_data['data']['seccode']['gen_time'],
                'captcha_output': verify_data['data']['seccode']['captcha_output'],
                'captcha_id': self.captcha_id
            }
            login_res = self.session.get(url=login_url, params=login_params, headers=self.headers, timeout=20).json()
            if login_res.get('result') == "success":
                logger.success(f"GeeTestV4 {init_json['data']['captcha_type']} & Login Verify Success：{verify_data['data']}")
                return login_res


def test(test_counts):
    success_counts = 0
    for i in range(1, test_counts + 1):
        geetest = GeeTestV4(captcha_id='be13c9e8983709233fd1ef8d70df68a0', risk_type='match')
        res = geetest.main()
        if res:
            success_counts += 1
            logger.debug(f'ACC：{success_counts / i}')
        logger.debug(f'第{i}次测试')


if __name__ == '__main__':
    geetest = GeeTestV4(captcha_id='be13c9e8983709233fd1ef8d70df68a0', risk_type='pencil')
    res = geetest.main()