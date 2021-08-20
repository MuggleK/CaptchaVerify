# -*- coding: utf-8 -*-
from flask import Flask, request
from flask import jsonify
import gc
from Yidun import YidunCracker

app = Flask(__name__)

crack_modle = None


@app.route('/yidun', methods=['GET'])
def post_to():
    try:
        sid = request.args.get('sid')
        width = request.args.get('width')
        referer = request.args.get('referer')
        # yz_type = request.args.get('yz_type')
    except Exception as e:
        print(e)
        return jsonify({'result': '参数有误'})
    # gc.disable()

    # try:
    result = YidunCracker('163', sid, width, referer).run()
    # except:
    #     result = '识别失败'

    gc.enable()
    return jsonify({'result': result})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='7123', debug=True)
