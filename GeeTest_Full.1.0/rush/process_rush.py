import redis,json


pool_4 = redis.ConnectionPool(host='127.0.0.1', port=6379, db=4,decode_responses=True, password="")
r_4 = redis.StrictRedis(connection_pool=pool_4)     # 已跑缓存

pool_5 = redis.ConnectionPool(host='127.0.0.1', port=6379, db=5,decode_responses=True, password="")
r_5 = redis.StrictRedis(connection_pool=pool_5)     # 初始缓存

new_rush = list(set(r_4.keys())^set(r_5.keys()))

pro_json = {}
for keys in new_rush:
    pro_json[keys] = r_4.get(keys)

print('新点选缓存筛选完毕')
with open('./rush/new_chinese.json','a',encoding='utf-8') as w:
    w.write(json.dumps(pro_json))

