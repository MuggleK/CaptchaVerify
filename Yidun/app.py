# -*-coding:utf-8-*-
from flask import Flask, request
import logging
from yidun import YidunCracker

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
LOGGER = logging.getLogger(__name__)


@app.route('/yidun', methods=['POST', 'GET'])
def parse_server():
    if request.method == 'POST':
        data = request.form
        sid = data.get('sid', None)
        width = data.get('width', None)
        referer = data.get('referer', None)
        host = data.get('host', None)
    elif request.method == 'GET':
        sid = request.args.get("sid")
        width = request.args.get("width")
        referer = request.args.get("referer")
        host = request.args.get("host")
    else:
        return '未支持的请求方式'
    res = {}
    if sid is None or '{' in sid:
        msg = "need sid param!"
        code = 400
        res['msg'] = msg
        res['code'] = code
        res['data'] = None
    else:
        res = YidunCracker('jiangsu', sid, width, referer, host).run()
    return res


if __name__ == '__main__':
    app.run(port=7123, host="0.0.0.0", threaded=True, debug=False)
