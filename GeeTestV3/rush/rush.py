import redis,json,os
from settings import redis_db_click

click_rush_pool = redis.ConnectionPool(host=redis_db_click.get('host'), port=redis_db_click.get('port'), db=redis_db_click.get('db'),
                                    decode_responses=True, password=redis_db_click.get('password'))
click_redis = redis.StrictRedis(connection_pool=click_rush_pool)

for file in os.listdir('../rush'):
    # print('开始导入缓存！')
    if file.split('.')[0] not in ['slide','rush','process_rush','settings','__pycache__']:
        path = f'../rush/{file}'
        print(path)
        with open(path,'r')as f:
            content = json.loads(f.read())
            for i in content.keys():
                click_redis.set(i,content.get(i))
        print(f'{file} 导入完成！')



