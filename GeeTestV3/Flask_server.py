# -*-coding:utf-8-*-
from flask import Flask, request
import logging
from main import CaptValidate

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
LOGGER = logging.getLogger(__name__)
geetest = CaptValidate()


@app.route('/captcha', methods=['POST', 'GET'])
def parse_server():
    if request.method == 'POST':
        data = request.form
        gt = data.get('gt', None)
        challenge = data.get('challenge', None)
        proxy = data.get('proxy', None)
    elif request.method == 'GET':
        gt = request.args.get("gt")
        challenge = request.args.get("challenge")
        proxy = request.args.get("proxy")
    else:
        return '未支持的请求方式'
    res = {}
    if gt is None or '{' in gt:
        msg = "need gt,challenge param!"
        code = 400
        res['msg'] = msg
        res['code'] = code
        res['data'] = None
    else:
        res = geetest.run(gt, challenge, proxy)
    return res


if __name__ == '__main__':
    app.run(port=5685, host="0.0.0.0", threaded=True, debug=False)
