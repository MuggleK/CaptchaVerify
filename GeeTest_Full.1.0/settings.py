# 打码接口
base_settings = {
    'Chinese':{
        # 'url':'http://127.0.0.1:5022/captcha',  # chinese
        'url':'http://127.0.0.1:5033/captcha',    # chinese_Semantic
        'headers':None
               },
    'Space_verify':{
        'url':'http://127.0.0.1:5055/captcha',
        'headers':None
                    },
    'Icon':{
        'url':'http://127.0.0.1:5044/captcha',
        'headers':None
             },
    'Nine_Click': {
        'url':'http://127.0.0.1:5099/captcha',
        'headers':{'Content-Type': 'image/jpeg'}
                   },
    'images_fail_path':'', #为空则不保存
}

# 存储错误缓存结果
save_fail_rush = True

# 日志保存
save_logs = True

# 是否开启调试
isDebug = True

# 点选识别缓存池
redis_db_click = {'host':'127.0.0.1','port':6379,'password':'','db':4}









