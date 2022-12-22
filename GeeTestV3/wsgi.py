# -*- coding: utf-8 -*-
# @Project : geetest_gct_click3.0
# @Time    : 2022/6/23 10:42
# @Author  : Changchuan.Pei
# @File    : wsgi.py

from Flask_server import app
import logging

gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
