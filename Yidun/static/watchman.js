function get_dd(protocol, pn, v, luv, conf) {
    var watchman = window.window.Watchman;
    var options = {
        apiServer: "ac.dun.163yun.com",
        auto: true,
        buildVersion: v,
        configHash: conf,
        lastUsedVersion: luv,
        merged: true,
        pn: pn,
        productNumber: pn,
        protocol: protocol,
        sConfig: conf,
        staticServer: "acstatic-dun.126.net",
        timeout: 0
    };

    new watchman(options);
    return window.d1
}

function sample(e, t) {
    var n = e.length;
    if (n <= t)
        return e;
    for (var i = [], r = 0, o = 0; o < n; o++)
        o >= r * (n - 1) / (t - 1) && (i.push(e[o]),
            r += 1);
    return i
}

function generateMouseTrack() {
    var move, points;
    move = [], points = [{
        'x': random(200, 300),
        'y': random(100, 200)
    }, {
        'x': random(600, 700),
        'y': random(300, 400)
    }];

    function sp(p, p2, pp) {
        var sump = Math.abs(p - p2);
        var x3 = Math.floor(Math.abs((pp - p)) / sump * 100);
        if (sump > 200) {
            if (x3 < 5 || x3 > 95) return 1;
            if (x3 < 10 || x3 > 90) return 2;
            if (x3 < 50 || x3 > 50) return 4
        } else if (sump > 150) {
            if (x3 <= 10 || x3 >= 90) return 1;
            if (x3 <= 25 || x3 >= 75) return 2;
            if (x3 <= 40 || x3 >= 70) return 3;
            if (x3 <= 50 || x3 >= 50) return 4;
        } else if (sump > 100) {
            if (x3 <= 10 || x3 >= 90) return 1;
            if (x3 <= 15 || x3 >= 70) return 2;
            if (x3 <= 25 || x3 >= 60) return 3;
            if (x3 <= 50 || x3 >= 50) return 4;
        } else if (sump > 70) {
            if (x3 <= 15 || x3 >= 95) return 1;
            if (x3 <= 20 || x3 >= 80) return 2;
            if (x3 <= 25 || x3 >= 70) return 3;
            if (x3 <= 50 || x3 >= 50) return 4;
        } else {
            if (x3 <= 15 || x3 >= 80) return 0;
            if (x3 <= 25 || x3 >= 65) return 1;
            if (x3 <= 50 || x3 >= 50) return 2;
        }
    }

    function computeTime(distance) {
        var t;
        switch (distance) {
            case 0:
                t = random(25, 69);
                break;
            case 1:
                t = random(13, 27);
                break;
            case 2:
                t = random(8, 15);
                break;
            case 3:
                t = random(7, 9);
                break;
            case 4:
                t = random(6, random(6, 9));
                break;
        }
        return t;
    }

    var x = 0, y = 0;
    var distanceX = 3;
    var distanceY = 1;
    // 档速
    var s0 = [0, 1, 1, 1];
    var s1 = [1, 1, 2, 2];
    var s2 = [2, 2, 3, 3];
    var s3 = [2, 3, 4, 4];
    var s4 = [3, 4, 4, 4];
    var speed = [s0, s1, s2, s3, s4];
    var sditance;
    x = points[0].x;
    y = points[0].y;
    var time = 0;

    var c = points.length;

    time += random(200, 300);
    move.push([x, y, time]);
    for (var i = 1; i < points.length; i++) {
        x2 = points[i].x;
        y2 = points[i].y;
        var o = Math.abs(points[i - 1].x - x2) / Math.abs(points[i - 1].y - y2);
        while (x - x2 != 0 || y - y2 != 0) {
            var xx = x - x2, yy = y - y2;
            var c = Math.abs(points[i - 1].x - x2) > Math.abs(points[i - 1].y - y2) ? 0 : 1;  //0=x 1=y谁是主线
            distanceX = sp(points[i - 1].x, x2, x);
            distancey = sp(points[i - 1].y, y2, y);
            if (!distanceX) {
                distanceX = random(1, 4)
            }
            var addX = speed[distanceX][random(0, speed[distanceX].length - 1)];
            if (xx != 0) {
                // if (addX > xx)
                // add = xx;
                // x - x2 > 0 ? addX : -addX;
                addX = xx > 0 ? -(addX > xx ? xx : addX) : (addX > Math.abs(xx) ? Math.abs(xx) : addX);
                x += addX;
            }
            var ss = Math.round(Math.abs(points[i - 1].x - x) / o);
            ss = points[i - 1].y > y2 ? -ss : ss;
            y = ss + points[i - 1].y;
            time += computeTime(distanceX);
            move.push([x, y, time])
        }
    }
    return sample(move, 50)
}

function acTokenCheck(protocol, pn, v, luv, conf, sid, wm_tid, wm_did, wm_ni) {
    var options = {
        apiServer: "ac.dun.163yun.com",
        auto: true,
        buildVersion: v,
        configHash: conf,
        lastUsedVersion: luv,
        merged: true,
        pn: pn,
        productNumber: pn,
        protocol: protocol,
        sConfig: conf,
        staticServer: "acstatic-dun.126.net",
        timeout: 0,
    };

    window["localStorage"][pn + ":WM_TID"] = wm_tid;
    window["localStorage"][pn + ":WM_NI"] = wm_ni;
    window["localStorage"][pn + ":WM_DID"] = wm_did;
    window["localStorage"][pn + ":WM_DIV"] = v;

    var watchman = window.window.Watchman;
    var encrypter = new watchman(options);

    var mouse_move, click_down, click_up, pointer_down, mouse_down, pointer_up, mouse_up, blur_event, focus_event;
    var trace = generateMouseTrack();

    blur_event = {
        isTrusted: true,
        target: {
            id: ''
        },
        timeStamp: 100000000 + Math.random() * 80000000,
        type: "blur",
    };
    var blur_flag;
    random(10, 20) > 15 ? document.blur(blur_event) : blur_flag = false;

    click_down = {
        button: 0,
        buttons: 1,
        isTrusted: true,
        clientX: trace[0][0],
        clientY: trace[0][1],
        target: {
            id: ''
        },
        timeStamp: 100000000 + Math.random() * 80000000,
        type: "click",
    };
    document.click(click_down);

    pointer_down = {
        button: 0,
        buttons: 1,
        isTrusted: true,
        clientX: trace[0][0],
        clientY: trace[0][1],
        pointerType: "mouse",
        target: {
            id: ''
        },
        timeStamp: 100000000 + Math.random() * 80000000,
        type: "pointerdown",
    };
    document.pointerdown(pointer_down);

    mouse_down = {
        button: 0,
        buttons: 1,
        isTrusted: true,
        clientX: trace[0][0],
        clientY: trace[0][1],
        timeStamp: 100000000 + Math.random() * 80000000,
        type: "mousedown",
    };
    document.mousedown(mouse_down);

    focus_event = {
        isTrusted: true,
        target: {
            id: ''
        },
        timeStamp: 100000000 + Math.random() * 80000000,
        type: "focus"
    };
    var focus_flag;
    random(10, 20) > 15 ? document.focus(focus_event) : focus_flag = false;

    for (var i = 0; i < trace.length; i++) {
        mouse_move = {
            button: 0,
            buttons: 0,
            isTrusted: true,
            clientX: trace[i][0],
            clientY: trace[i][1],
            timeStamp: 100000000 + Math.random() * 80000000,
            type: "mousemove",
        };
        document.mousemove(mouse_move);
    }

    pointer_up = {
        button: 0,
        buttons: 0,
        isTrusted: true,
        clientX: trace[trace.length - 1][0],
        clientY: trace[trace.length - 1][1],
        timeStamp: 100000000 + Math.random() * 80000000,
        pointerType: "mouse",
        type: "pointerup",
    };
    document.pointerup(pointer_up);
    mouse_up = {
        button: 0,
        buttons: 0,
        isTrusted: true,
        clientX: trace[trace.length - 1][0],
        clientY: trace[trace.length - 1][1],
        timeStamp: 100000000 + Math.random() * 80000000,
        type: "mouseup",
    };
    document.mouseup(mouse_up);

    click_up = {
        button: 0,
        buttons: 0,
        isTrusted: true,
        clientX: trace[trace.length - 1][0],
        clientY: trace[trace.length - 1][1],
        target: {
            id: ''
        },
        timeStamp: 100000000 + Math.random() * 80000000,
        type: "click",
    };
    document.click(click_up);

    var getAcToken = function (obj) {
        window.acToken = obj
    };

    var getNike = function(obj) {
        window.nike = obj
    };

    encrypter._getToken(sid, getAcToken, 750);
    encrypter._getNdInfo(getNike);
    return {
        d: window.d2,
        acToken: window.acToken,
        wm_nike: window.nike
    }
}

