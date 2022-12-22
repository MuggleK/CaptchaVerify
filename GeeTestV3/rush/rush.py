import os
import json

from settings import click_redis

for file in os.listdir('../rush'):
    print('开始导入缓存！')
    if file.split('.')[0] in ['all']:
        path = f'../rush/{file}'
        with open(path, 'r')as f:
            content = json.loads(f.read())
            for i in content.keys():
                click_redis.set(i, content.get(i))
        print(f'{file} 导入完成！')
# keys = click_redis.keys()
# with open('all.json','w',encoding='utf8') as f:
#     item = {}
#     for i in keys:
#         item[i] = click_redis.get(i)
#     f.write(json.dumps(item))
