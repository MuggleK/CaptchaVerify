var t = {};

!function () {
    function n(e, t) {
        function n(e, t) {
            return e.charCodeAt(Math.floor(t % e.length))
        }

        function i(e, t) {
            return t.split("").map(function (t, i) {
                return t.charCodeAt(0) ^ n(e, i)
            })
        }

        return t = i(e, t),
            _(t)
    }

    __toByte = function (e) {
        function t(t) {
            return e.apply(this, arguments)
        }

        return t.toString = function () {
            return e.toString()
        }
            ,
            t
    }(function (e) {
        if (e < -128)
            return __toByte(128 - (-128 - e));
        if (e >= -128 && e <= 127)
            return e;
        if (e > 127)
            return __toByte(-129 + e - 127);
        throw new Error("1001")
    });
    var i = function (e, t) {
            return __toByte(e + t)
        }
        , r = function (e, t) {
            if (null == e)
                return null;
            if (null == t)
                return e;
            for (var n = [], r = t.length, o = 0, a = e.length; o < a; o++)
                n[o] = i(e[o], t[o % r]);
            return n
        }
        , o = function (e, t) {
            return e = __toByte(e),
                t = __toByte(t),
                __toByte(e ^ t)
        }
        , a = function (e, t) {
            if (null == e || null == t || e.length != t.length)
                return e;
            for (var n = [], i = e.length, r = 0, a = i; r < a; r++)
                n[r] = o(e[r], t[r]);
            return n
        }
        , l = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f"]
        , s = function (e) {
            var t = [];
            return t.push(l[e >>> 4 & 15]),
                t.push(l[15 & e]),
                t.join("")
        }
        , u = function (e) {
            var t = e.length;
            if (null == e || t < 0)
                return new String("");
            for (var n = [], i = 0; i < t; i++)
                n.push(s(e[i]));
            return n.join("")
        }
        , f = function (e) {
            if (null == e || 0 == e.length)
                return [];
            for (var t = new String(e), n = [], i = t.length / 2, r = 0, o = 0; o < i; o++) {
                var a = parseInt(t.charAt(r++), 16) << 4
                    , l = parseInt(t.charAt(r++), 16);
                n[o] = __toByte(a + l)
            }
            return n
        }
        , j = function (e) {
            if (null == e || void 0 == e)
                return e;
            for (var t = encodeURIComponent(e), n = [], i = t.length, r = 0; r < i; r++)
                if ("%" == t.charAt(r)) {
                    if (!(r + 2 < i))
                        throw new Error("1009");
                    n.push(f(t.charAt(++r) + "" + t.charAt(++r))[0])
                } else
                    n.push(t.charCodeAt(r));
            return n
        }
        , c = function (e) {
            var t = [];
            return t[0] = e >>> 24 & 255,
                t[1] = e >>> 16 & 255,
                t[2] = e >>> 8 & 255,
                t[3] = 255 & e,
                t
        }
        , d = function (e) {
            var t = c(e);
            return u(t)
        }
        , h = function (e, t, n) {
            var i = [];
            if (null == e || 0 == e.length)
                return i;
            if (e.length < n)
                throw new Error("1003");
            for (var r = 0; r < n; r++)
                i[r] = e[t + r];
            return i
        }
        , p = function (e, t, n, i, r) {
            if (null == e || 0 == e.length)
                return n;
            if (null == n)
                throw new Error("1004");
            if (e.length < r)
                throw new Error("1003");
            for (var o = 0; o < r; o++)
                n[i + o] = e[t + o];
            return n
        }
        , y = function (e) {
            for (var t = [], n = 0; n < e; n++)
                t[n] = 0;
            return t
        }
        , v = function (e) {
            return null == e || void 0 == e || "" == e
        }
        , g = function () {
            return ["i", "/", "x", "1", "X", "g", "U", "0", "z", "7", "k", "8", "N", "+", "l", "C", "p", "O", "n", "P", "r", "v", "6", "\\", "q", "u", "2", "G", "j", "9", "H", "R", "c", "w", "T", "Y", "Z", "4", "b", "f", "S", "J", "B", "h", "a", "W", "s", "t", "A", "e", "o", "M", "I", "E", "Q", "5", "m", "D", "d", "V", "F", "L", "K", "y"]
        }
        , b = function () {
            return "3"
        }
        , m = function (e, t, n) {
            var i, r, o, a = g(), l = b(), s = [];
            if (1 == n)
                i = e[t],
                    r = 0,
                    o = 0,
                    s.push(a[i >>> 2 & 63]),
                    s.push(a[(i << 4 & 48) + (r >>> 4 & 15)]),
                    s.push(l),
                    s.push(l);
            else if (2 == n)
                i = e[t],
                    r = e[t + 1],
                    o = 0,
                    s.push(a[i >>> 2 & 63]),
                    s.push(a[(i << 4 & 48) + (r >>> 4 & 15)]),
                    s.push(a[(r << 2 & 60) + (o >>> 6 & 3)]),
                    s.push(l);
            else {
                if (3 != n)
                    throw new Error("1010");
                i = e[t],
                    r = e[t + 1],
                    o = e[t + 2],
                    s.push(a[i >>> 2 & 63]),
                    s.push(a[(i << 4 & 48) + (r >>> 4 & 15)]),
                    s.push(a[(r << 2 & 60) + (o >>> 6 & 3)]),
                    s.push(a[63 & o])
            }
            return s.join("")
        }
        , _ = function (e) {
            if (null == e || void 0 == e)
                return null;
            if (0 == e.length)
                return "";
            var t = 3;
            try {
                for (var n = [], i = 0; i < e.length;) {
                    if (!(i + t <= e.length)) {
                        n.push(m(e, i, e.length - i));
                        break
                    }
                    n.push(m(e, i, t)),
                        i += t
                }
                return n.join("")
            } catch (r) {
                throw new Error("1010")
            }
        }
        , w = function (e) {
            return _(j(e))
        }
        ,
        T = [0, 1996959894, 3993919788, 2567524794, 124634137, 1886057615, 3915621685, 2657392035, 249268274, 2044508324, 3772115230, 2547177864, 162941995, 2125561021, 3887607047, 2428444049, 498536548, 1789927666, 4089016648, 2227061214, 450548861, 1843258603, 4107580753, 2211677639, 325883990, 1684777152, 4251122042, 2321926636, 335633487, 1661365465, 4195302755, 2366115317, 997073096, 1281953886, 3579855332, 2724688242, 1006888145, 1258607687, 3524101629, 2768942443, 901097722, 1119000684, 3686517206, 2898065728, 853044451, 1172266101, 3705015759, 2882616665, 651767980, 1373503546, 3369554304, 3218104598, 565507253, 1454621731, 3485111705, 3099436303, 671266974, 1594198024, 3322730930, 2970347812, 795835527, 1483230225, 3244367275, 3060149565, 1994146192, 31158534, 2563907772, 4023717930, 1907459465, 112637215, 2680153253, 3904427059, 2013776290, 251722036, 2517215374, 3775830040, 2137656763, 141376813, 2439277719, 3865271297, 1802195444, 476864866, 2238001368, 4066508878, 1812370925, 453092731, 2181625025, 4111451223, 1706088902, 314042704, 2344532202, 4240017532, 1658658271, 366619977, 2362670323, 4224994405, 1303535960, 984961486, 2747007092, 3569037538, 1256170817, 1037604311, 2765210733, 3554079995, 1131014506, 879679996, 2909243462, 3663771856, 1141124467, 855842277, 2852801631, 3708648649, 1342533948, 654459306, 3188396048, 3373015174, 1466479909, 544179635, 3110523913, 3462522015, 1591671054, 702138776, 2966460450, 3352799412, 1504918807, 783551873, 3082640443, 3233442989, 3988292384, 2596254646, 62317068, 1957810842, 3939845945, 2647816111, 81470997, 1943803523, 3814918930, 2489596804, 225274430, 2053790376, 3826175755, 2466906013, 167816743, 2097651377, 4027552580, 2265490386, 503444072, 1762050814, 4150417245, 2154129355, 426522225, 1852507879, 4275313526, 2312317920, 282753626, 1742555852, 4189708143, 2394877945, 397917763, 1622183637, 3604390888, 2714866558, 953729732, 1340076626, 3518719985, 2797360999, 1068828381, 1219638859, 3624741850, 2936675148, 906185462, 1090812512, 3747672003, 2825379669, 829329135, 1181335161, 3412177804, 3160834842, 628085408, 1382605366, 3423369109, 3138078467, 570562233, 1426400815, 3317316542, 2998733608, 733239954, 1555261956, 3268935591, 3050360625, 752459403, 1541320221, 2607071920, 3965973030, 1969922972, 40735498, 2617837225, 3943577151, 1913087877, 83908371, 2512341634, 3803740692, 2075208622, 213261112, 2463272603, 3855990285, 2094854071, 198958881, 2262029012, 4057260610, 1759359992, 534414190, 2176718541, 4139329115, 1873836001, 414664567, 2282248934, 4279200368, 1711684554, 285281116, 2405801727, 4167216745, 1634467795, 376229701, 2685067896, 3608007406, 1308918612, 956543938, 2808555105, 3495958263, 1231636301, 1047427035, 2932959818, 3654703836, 1088359270, 936918e3, 2847714899, 3736837829, 1202900863, 817233897, 3183342108, 3401237130, 1404277552, 615818150, 3134207493, 3453421203, 1423857449, 601450431, 3009837614, 3294710456, 1567103746, 711928724, 3020668471, 3272380065, 1510334235, 755167117]
        , S = function (e) {
            var t = 4294967295;
            if (null != e)
                for (var n = 0; n < e.length; n++) {
                    var i = e[n];
                    t = t >>> 8 ^ T[255 & (t ^ i)]
                }
            return d(4294967295 ^ t, 8)
        }
        , E = function (e) {
            return S(null == e ? [] : j(e))
        }
        ,
        R = [120, 85, -95, -84, 122, 38, -16, -53, -11, 16, 55, 3, 125, -29, 32, -128, -94, 77, 15, 106, -88, -100, -34, 88, 78, 105, -104, -90, -70, 90, -119, -28, -19, -47, -111, 117, -105, -62, -35, 2, -14, -32, 114, 23, -21, 25, -7, -92, 96, -103, 126, 112, -113, -65, -109, -44, 47, 48, 86, 75, 62, -26, 72, -56, -27, 66, -42, 63, 14, 92, 59, -101, 19, -33, 12, -18, -126, -50, -67, 42, 7, -60, -81, -93, -86, 40, -69, -37, 98, -63, -59, 108, 46, -45, 93, 102, 65, -79, 73, -23, -46, 37, -114, -15, 44, -54, 99, -10, 60, -96, 76, 26, 61, -107, 18, -116, -55, -40, 57, -76, -82, 45, 0, -112, -77, 29, 43, -30, 109, -91, -83, 107, 101, 81, -52, -71, 84, 36, -41, 68, 39, -75, -122, -6, 11, -80, -17, -74, -73, 35, 49, -49, -127, 80, 103, 79, -25, 52, -43, 56, 41, -61, -24, 17, -118, 115, -38, 8, -78, 33, -85, -106, 58, -98, -108, 94, 116, -125, -51, -9, 71, 82, 87, -115, 9, 69, -123, 123, -117, 113, -22, -124, -87, 64, 13, 21, -89, -2, -99, -97, 1, -4, 34, 20, 83, 119, 30, -12, -110, -66, 118, -48, 6, -36, 104, -58, -102, 97, 5, -20, 31, -72, 70, -39, 67, -68, -57, 110, 89, 51, 10, -120, 28, 111, 127, 22, -3, 54, 53, -1, 100, 74, 50, 91, 27, -31, -5, -64, 124, -121, 24, -13, 95, 121, -8, 4]
        , C = 4
        , k = 4
        , O = 4
        , X = 4
        , $ = function (e) {
            var t = [];
            if (null == e || void 0 == e || 0 == e.length)
                return y(k);
            if (e.length >= k)
                return h(e, 0, k);
            for (var n = 0; n < k; n++)
                t[n] = e[n % e.length];
            return t
        }
        , I = function (e) {
            if (null == e || void 0 == e || 0 == e.length)
                return y(C);
            var t = e.length
                , n = 0;
            n = t % C <= C - O ? C - t % C - O : 2 * C - t % C - O;
            var i = [];
            p(e, 0, i, 0, t);
            for (var r = 0; r < n; r++)
                i[t + r] = 0;
            var o = c(t);
            return p(o, 0, i, t + n, O),
                i
        }
        , x = function (e) {
            if (null == e || e.length % C != 0)
                throw new Error("1005");
            for (var t = [], n = 0, i = e.length / C, r = 0; r < i; r++) {
                t[r] = [];
                for (var o = 0; o < C; o++)
                    t[r][o] = e[n++]
            }
            return t
        }
        , A = function (e) {
            var t = e >>> 4 & 15
                , n = 15 & e
                , i = 16 * t + n;
            return R[i]
        }
        , P = function (e) {
            if (null == e)
                return null;
            for (var t = [], n = 0, i = e.length; n < i; n++)
                t[n] = A(e[n]);
            return t
        }
        , N = function () {
            for (var e = [], t = 0; t < X; t++) {
                var n = 256 * Math.random();
                n = Math.floor(n),
                    e[t] = __toByte(n)
            }
            return e
        }
        , M = function (e, t) {
            if (null == e)
                return null;
            for (var n = __toByte(t), i = [], r = e.length, a = 0; a < r; a++)
                i.push(o(e[a], n));
            return i
        }
        , D = function (e, t) {
            if (null == e)
                return null;
            for (var n = __toByte(t), r = [], o = e.length, a = 0; a < o; a++)
                r.push(i(e[a], n));
            return r
        }
        , M = function (e, t) {
            if (null == e)
                return null;
            for (var n = __toByte(t), i = [], r = e.length, a = 0; a < r; a++)
                i.push(o(e[a], n));
            return i
        }
        , L = function (e) {
            var t = M(e, 56)
                , n = D(t, -40)
                , i = M(n, 103);
            return i
        }
        , Y = function (e, t) {
            null == e && (e = []);
            var n = N();
            t = $(t),
                t = a(t, $(n)),
                t = $(t);
            var i = t
                , o = I(e)
                , l = x(o)
                , s = [];
            p(n, 0, s, 0, X);
            for (var u = l.length, f = 0; f < u; f++) {
                var j = L(l[f])
                    , c = a(j, t)
                    , d = r(c, i);
                c = a(d, i);
                var h = P(c);
                h = P(h),
                    p(h, 0, s, f * C + X, C),
                    i = h
            }
            return s
        }
        , B = function (e) {
            var t = "14731382d816714fC59E47De5dA0C871D3F";
            if (null == t || void 0 == t)
                throw new Error("1008");
            null != e && void 0 != e || (e = "");
            var n = e + E(e)
                , i = j(n)
                , r = j(t)
                , o = Y(i, r);
            return _(o)
        };
    t.eypt = B,
        t.xor_encode = n,
        t.toByte = __toByte,
        t.str2Bytes = j,
        t.arrayCopy = h,
        t.arrayCopy2 = p,
        t.createEmptyArray = y,
        t.isEmptyString = v,
        t.base64Encode = w,
        t.getStringCRC32 = E,
        t.toByte = __toByte
}();

function uuid(e, t) {
    var n = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz".split("")
        , a = []
        , i = void 0;
    if (t = t || n.length,
        e)
        for (i = 0; i < e; i++)
            a[i] = n[0 | Math.random() * t];
    else {
        var r = void 0;
        for (a[8] = a[13] = a[18] = a[23] = "-",
                 a[14] = "4",
                 i = 0; i < 36; i++)
            a[i] || (r = 0 | 16 * Math.random(),
                a[i] = n[19 === i ? 3 & r | 8 : r])
    }
    return a.join("")
}

function get_cb() {
    var e = uuid(32);
    return s(e)
}

function getmove() {
    return JSON.stringify(traceData);
}

function init(tk) {
    token = tk;
    beginTime = new Date().getTime();
    pointsStack = [];
    traceData = [];
    move2 = [];
    po = [];
    return token;
}

function getpoint() {
    return JSON.stringify(pointsStack)
}

function addPoint(x, y) {
    // e = {x, y} 图片范围的坐标
    var t = x, n = y
        , p = f(token, [Math.round(t), Math.round(n), new Date().getTime() - beginTime] + "");
    pointsStack.push(p);
}

function trackMoving(x, y) {
    // 鼠标移动轨迹
    var n = x, i = y
        , r = f(token, [Math.round(n), Math.round(i), new Date().getTime() - beginTime] + "");
    traceData.push(r) // f = n; 图片内的移动轨迹
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

function random(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

function encryptPoint(points) {
    var click = [];
    var move = [];
    (function () {
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
        time += random(2, 10);
        click.push([x, y, time] + '');

        time += random(200, 300);
        move.push([x, y, time] + '');
        for (var i = 1; i < points.length; i++) {
            x2 = points[i].x;
            y2 = points[i].y;
            var o = Math.abs(points[i - 1].x - x2) / Math.abs(points[i - 1].y - y2);
            while (x - x2 !== 0 || y - y2 !== 0) {
                var xx = x - x2, yy = y - y2;
                var c = Math.abs(points[i - 1].x - x2) > Math.abs(points[i - 1].y - y2) ? 0 : 1;  //0=x 1=y谁是主线
                distanceX = sp(points[i - 1].x, x2, x);
                distancey = sp(points[i - 1].y, y2, y);
                if (!distanceX) {
                    distanceX = random(2, 4)
                }
                var addX = speed[distanceX][random(0, speed[distanceX].length - 1)];
                if (xx !== 0) {
                    // if (addX > xx)
                    // add=xx;
                    // x - x2 > 0 ? addX : - addX;
                    addX = xx > 0 ? -(addX > xx ? xx : addX) : (addX > Math.abs(xx) ? Math.abs(xx) : addX);
                    x += addX;
                }
                var ss = Math.round(Math.abs(points[i - 1].x - x) / o);
                ss = points[i - 1].y > y2 ? -ss : ss;
                y = ss + points[i - 1].y;
                time += computeTime(distanceX);
                move.push([x, y, time] + '')
            }
            time += random(200, 300);
            click.push([x, y, time] + '')
        }

    })();
    for (var i = 0; i < move.length; i++) {
        move2.push(move[i]);
        traceData.push(f(token, move[i]))
    }
    for (var j = 0; j < click.length; j++) {
        pointsStack.push(f(token, click[j]));
        po.push(click[j])
    }
    return traceData.length
}

let lodash = require('./static/lodash');

function encryptTrace(distance) {
    let x = [[4, 0, 136], [5, 0, 141], [7, 0, 145], [9, 0, 153], [10, 0, 157], [14, 0, 166], [15, 0, 169], [18, 0, 177], [19, 0, 181], [22, 0, 188], [23, 0, 195], [25, 0, 197], [26, 0, 200], [30, 0, 208], [34, 0, 216], [37, 0, 224], [39, 0, 229], [43, 0, 236], [45, 0, 242], [47, 0, 245], [51, 0, 253], [52, 0, 256], [55, 0, 265], [57, 0, 273], [58, 0, 277], [59, 0, 281], [61, 0, 289], [63, 0, 297], [64, 0, 300], [66, 0, 308], [68, 0, 315], [71, 0, 324], [72, 0, 329], [74, 0, 336], [76, 0, 343], [77, 0, 345], [78, 0, 348], [80, 0, 356], [81, 0, 363], [83, 0, 364], [84, 0, 372], [85, 0, 377], [86, 0, 380], [87, 0, 386], [88, 0, 389], [90, 0, 397], [91, 0, 404], [93, 0, 410], [94, 0, 412], [96, 0, 421], [98, 0, 429], [99, 0, 437], [101, 0, 444], [104, 0, 453], [105, 0, 456], [106, 0, 463], [107, 0, 465], [109, 0, 473], [110, 0, 476], [111, 0, 480], [113, 0, 486], [114, 0, 488], [115, 1, 495], [116, 1, 496], [118, 1, 499], [120, 1, 506], [121, 1, 514], [123, 1, 522], [124, 1, 526], [125, 1, 535], [126, 1, 538], [127, 1, 545], [128, 1, 554], [129, 1, 563], [130, 1, 570], [131, 1, 576], [132, 1, 579], [133, 1, 586], [134, 1, 592], [135, 1, 600], [136, 1, 608], [138, 1, 618], [139, 1, 637], [140, 1, 677], [141, 1, 696], [142, 1, 703], [143, 1, 713], [144, 1, 721], [145, 1, 738], [145, 2, 751], [146, 2, 758], [147, 2, 773], [148, 2, 790], [149, 2, 822], [150, 2, 834], [151, 2, 842], [152, 2, 851], [153, 2, 869], [154, 2, 890], [155, 2, 901], [156, 2, 918], [157, 2, 935], [158, 2, 951], [159, 2, 958], [160, 2, 990], [161, 2, 1022], [162, 2, 1041], [163, 2, 1057], [164, 2, 1078], [165, 2, 1097], [166, 2, 1117], [167, 2, 1134], [168, 2, 1138], [169, 2, 1153], [171, 2, 1164], [172, 2, 1172], [173, 2, 1179], [174, 2, 1187], [176, 2, 1204], [177, 2, 1219], [178, 2, 1236], [179, 2, 1252], [180, 2, 1254], [181, 2, 1273], [182, 2, 1294], [183, 2, 1339], [184, 2, 1347], [185, 2, 1362], [186, 2, 1375], [187, 2, 1885], [188, 2, 1897], [189, 2, 1906], [190, 2, 1919], [192, 2, 1922], [193, 2, 1931], [194, 2, 1934], [196, 2, 1947], [197, 2, 1956], [199, 2, 1970], [200, 2, 1990], [201, 2, 2013], [202, 2, 2114], [203, 2, 2123], [204, 2, 2142], [205, 2, 2177], [206, 2, 2200], [207, 2, 2210], [208, 2, 2221], [209, 2, 2234], [210, 2, 2251], [211, 2, 2271], [212, 2, 2286], [213, 2, 2301], [214, 2, 2306], [215, 2, 2322], [216, 2, 2334], [217, 2, 2382], [218, 2, 2421], [219, 2, 2462], [220, 2, 2471], [221, 2, 2501], [222, 2, 2521], [223, 2, 2554], [224, 2, 2582], [225, 2, 2610], [226, 2, 2646], [227, 2, 2682], [228, 2, 2686], [229, 2, 2714], [230, 2, 2778], [231, 2, 2810], [232, 2, 2818], [232, 3, 2827], [233, 3, 2874], [234, 3, 2885], [235, 3, 2906], [236, 4, 2923], [237, 4, 2966], [238, 4, 2985], [239, 4, 3010], [240, 4, 3022], [241, 4, 3078], [242, 4, 3110], [243, 5, 3126], [244, 5, 3198], [245, 5, 3210], [246, 5, 3230], [247, 5, 3313], [248, 6, 3330], [249, 6, 3402], [250, 6, 3462], [251, 6, 3522], [252, 6, 3542], [253, 6, 3573], [254, 6, 3661], [255, 6, 3922], [256, 6, 3941], [257, 6, 3952], [258, 6, 3969], [257, 6, 4358], [256, 6, 4368], [255, 6, 4393], [254, 6, 4425], [253, 6, 4446], [252, 6, 4469], [251, 6, 4505], [250, 6, 4538], [249, 6, 4613], [248, 6, 4622], [247, 6, 4686], [246, 6, 4722], [245, 6, 4762], [244, 6, 4779], [243, 6, 4821], [242, 6, 4853], [241, 6, 4882], [240, 6, 4938], [239, 6, 4961], [238, 6, 4990], [237, 6, 5034], [237, 7, 5042], [237, 8, 5054], [236, 8, 5068], [235, 8, 5577], [235, 9, 5934], [236, 9, 6062], [237, 9, 6114], [238, 9, 6189], [239, 9, 6210], [240, 9, 6230], [241, 9, 6265], [242, 9, 6293], [242, 10, 6322], [243, 10, 6466], [244, 10, 6671]]
        , moves = [];
    let x_total_time = lodash.last(x)[2];
    let x_total_length = lodash.last(x)[0];
    let time = lodash.random(1000, 2000);

    moves.push([x[0][0], x[0][1], x[0][2]]);
    for (let i = 1; i < x.length; i++) {
        moves.push([
            Math.round(x[i][0] / x_total_length * distance),
            x[i][1],
            Math.round(x[i][2] / x_total_time * time)
        ]);
    }
    for (let j = 0; j < moves.length; j++) {
        traceData.push(f(token, moves[j] + ""))
    }
    return moves[moves.length - 1][0] - moves[0][0]
}

function getmove2() {
    return JSON.stringify(move2);
}

function getmove2_50() {
    return JSON.stringify(sample(move2, 50)) + '|' + JSON.stringify(po);
}

var s = t.eypt;
var f = t.xor_encode;

var beginTime;
// 点击数据
var pointsStack = [];
// 移动轨迹数据
var traceData = [];
var move2 = [];
var po = [];

function senseEncrypt(token, points) {
    init(token);
    encryptPoint(points);
    return JSON.stringify({
        d: "",
        m: s(sample(traceData, 50).join(':')),
        p: s(f(token, [points[1]["x"], points[1]["y"], random(500, 1000)] + "")),
        ext: s(f(token, "1," + traceData.length))
    })
}

function sliderEncrypt(token, distance, width) {
    init(token);
    var x = encryptTrace(distance);
    var n = sample(traceData, 50),
        r = s(f(token, parseInt(x + "px", 10) / width * 100 + ""));
    return JSON.stringify({
        d: s(n.join(":")),
        m: "",
        p: r,
        ext: s(f(token, "1," + traceData.length))
    })
}

function clickEncrypt(token, points) {
    init(token);
    encryptPoint(points);
    return JSON.stringify({
        d: "",
        m: s(sample(traceData, 50).join(":")),
        p: s(pointsStack.join(":")),
        ext: s(f(token, pointsStack.length + "," + traceData.length))
    })
}

function exchangeEncrypt(token, points, pos) {
    init(token);
    encryptPoint(points);
    return JSON.stringify({
        d: "",
        m: s(sample(traceData, 50).join(':')),
        p: s(f(token, pos)),
        ext: s(f(token, "1," + traceData.length))
    })
}

function N(e) {
    var t = {
        "\\": "-",
        "/": "_",
        "+": "."
    };
    return e.replace(/[\\\/+]/g, function (e) {
        return t[e]
    })
}

function encryptValidate(validate, fp) {
    return N(s(validate + "::" + fp))
}
