import redis


# 打码接口
base_settings = {
    'Chinese': {
        'url': 'http://handidata.net:5223/captcha',
        'headers': None
    },
    'Space_verify': {
        'url': 'http://handidata.net:5711/captcha',
        'headers': None
    },
    'Icon': {
        'url': 'http://handidata.net:5978/captcha',
        'headers': None
    },
    'Nine_Click': {
        'url': 'handidata.net:5479/captcha',
        'headers': {
            'Content-Type': 'image/jpeg'
        }
    },
    'images_fail_path': '',  # 为空则不保存
}

# 存储错误缓存结果
save_fail_rush = False

# 日志保存
save_logs = True

# 是否开启调试
isDebug = True

# 点选识别缓存池
redis_db_click = {'host': '127.0.0.1', 'port': 6379, 'password': 'mugglek..aa', 'db': 4}

# 极验点选缓存池
click_rush_pool = redis.ConnectionPool(
    host=redis_db_click['host'],
    port=redis_db_click['port'],
    db=redis_db_click['db'],
    decode_responses=True,
    password=redis_db_click['password']
)
click_redis = redis.StrictRedis(connection_pool=click_rush_pool)
