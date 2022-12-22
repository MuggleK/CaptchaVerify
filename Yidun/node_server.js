const logger = require('./static/logger').logger('node_server.js', 'debug');
const express = require('express');
const bodyParser = require('body-parser');
const multipart = require('connect-multiparty');
const multipartMiddleware = multipart();
const app = express();
app.use(bodyParser.json({limit:'100mb'}));
app.use(bodyParser.urlencoded({ limit:'100mb', extended: true }));
const { get_cb, clickEncrypt, encryptValidate } = require('./static/core');
const { getFingerprint, get_dd, acTokenCheck } = require('./static/source_watchman');


app.post('/core/cb', multipartMiddleware, function (req, res) {
    try {
        let cb = get_cb();
        logger.info("cb：" + cb)
        res.json({
            code: 200,
            errorMsg: 'success',
            data: cb
        })
    } catch (e) {
        console.error(e);
        res.json({
            code: 500,
            errorMsg: 'cb encrypt internal error',
            data: null
        })
    }

});

app.post('/core/clickEncrypt', multipartMiddleware, function (req, res) {
    let token = req.body.token
    let points = req.body.points
    if (!(token && points)) {
        res.json({
            code: 404,
            errorMsg: 'clickEncrypt param error',
            data: null
        });
    } else {
        try {
            let result = clickEncrypt(token, points);
            logger.info("clickEncrypt：" + result)
            res.json({
                code: 200,
                errorMsg: 'success',
                data: result
            })
        } catch (e) {
            console.error(e);
            res.json({
                code: 500,
                errorMsg: 'clickEncrypt internal error',
                data: null
            })
        }
    }
});

app.post('/core/encryptValidate', multipartMiddleware, function (req, res) {
    let validate = req.body.validate
    let fingerprint = req.body.fingerprint
    if (!(validate && fingerprint)) {
        res.json({
            code: 404,
            errorMsg: 'encryptValidate param error',
            data: null
        });
    } else {
        try {
            let result = encryptValidate(validate, fingerprint);
            logger.info("encryptValidate：" + result)
            res.json({
                code: 200,
                errorMsg: 'success',
                data: result
            })
        } catch (e) {
            console.error(e);
            res.json({
                code: 500,
                errorMsg: 'encryptValidate internal error',
                data: null
            })
        }
    }
});

app.post('/watchman/fp', multipartMiddleware, function (req, res) {
    let host = req.body.host
    if (!(host)) {
        res.json({
            code: 404,
            errorMsg: 'getFingerprint param error',
            data: null
        });
    } else {
        try {
            let result = getFingerprint(host);
            logger.info("getFingerprint：" + result)
            res.json({
                code: 200,
                errorMsg: 'success',
                data: result
            })
        } catch (e) {
            console.error(e);
            res.json({
                code: 500,
                errorMsg: 'getFingerprint internal error',
                data: null
            })
        }
    }
});

app.post('/watchman/dd', multipartMiddleware, function (req, res) {
    let protocol = req.body.protocol
    let pn = req.body.pn
    let v = req.body.v
    let luv = req.body.luv
    let conf = req.body.conf
    if (!(protocol && pn && v && luv && conf)) {
        res.json({
            code: 404,
            errorMsg: 'get_dd param error',
            data: null
        });
    } else {
        try {
            let result = get_dd(protocol, pn, v, luv, conf);
            logger.info("get_dd：" + JSON.stringify(result))
            res.json({
                code: 200,
                errorMsg: 'success',
                data: result
            })
        } catch (e) {
            console.error(e);
            res.json({
                code: 500,
                errorMsg: 'get_dd internal error',
                data: null
            })
        }
    }
});

app.post('/watchman/acToken', multipartMiddleware, function (req, res) {
    let protocol = req.body.protocol
    let pn = req.body.pn
    let v = req.body.v
    let luv = req.body.luv
    let conf = req.body.conf
    let sid = req.body.sid
    let wm_tid = req.body.wm_tid
    let wm_did = req.body.wm_did
    let wm_ni = req.body.wm_ni
    if (!(protocol && pn && v && luv && conf && sid && wm_tid && wm_did && wm_ni)) {
        res.json({
            code: 404,
            errorMsg: 'acTokenCheck param error',
            data: null
        });
    } else {
        try {
            let result = acTokenCheck(protocol, pn, v, luv, conf, sid, wm_tid, wm_did, wm_ni);
            logger.info("acTokenCheck：" + JSON.stringify(result))
            res.json({
                code: 200,
                errorMsg: 'success',
                data: result
            })
        } catch (e) {
            console.error(e);
            res.json({
                code: 500,
                errorMsg: 'acTokenCheck internal error',
                data: null
            })
        }
    }
});

/**************************************启动服务**************************************/
const server = app.listen(5683, function() {
    let host = server.address().address;
    let port = server.address().port;
    logger.debug(`易盾加密服务启动, 监听地址为: http://${host}:${port}`)
});
