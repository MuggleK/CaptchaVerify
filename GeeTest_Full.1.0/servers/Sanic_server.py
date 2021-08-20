# -*- coding: utf-8 -*-

import json
from sanic import Sanic
from sanic.response import text, json
from Geestest import Capt_validate
import warnings
warnings.filterwarnings("ignore")


app = Sanic(__name__)


@app.route("/")
async def root(request):
    return text('Welcome to Geestest Captcha Cracker System')


@app.route("/geetest/verify", methods=["GET"])
async def v2(request):
    params = request.args
    if all(key in params for key in {'gt', 'challenge'}):
        gt = params.get('gt', '')
        challenge = params.get('challenge', '')
        proxy = params.get('proxy','')
        result = await Capt_validate(gt, challenge, proxy).run()
        return json(result)
    else:
        return json({
            'code': 400,
            'errorMsg': 'param error',
            'data': None
        })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8044,debug=False)
