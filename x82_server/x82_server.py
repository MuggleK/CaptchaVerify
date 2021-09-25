import requests
import execjs
from urllib.parse import quote
from loguru import logger


def get_ua():
    res = requests.post('http://127.0.0.1:7777/x82_ua').json()
    return res.get('ua')


with open('./catvm.build.js','r',encoding='utf-8')as f:
        ctx = execjs.compile(f.read().encode('utf-8').decode('gbk',errors='ignore'))
# encrypt_ua = ctx.call('slide_ua')
encrypt_ua = get_ua()
x5secdata = '5e0c8e1365474455070961b803bd560607b52cabf5960afff39b64ce58073f78f68ede033dd239842063c29628191423773f1e4d712042da0b04859e7922f0cd5a49cf810c8ea8c78076c37459cb8a51dc54a2268bb1915d83322256e1c27511e789e34f9a8d5ae0365a3fe8d0fffe6d823d444dc5f43ac275b3c69b848882339cadbc42a0c0b8db6902b963ce648992a01242bb78a70afee55467d2fba8164692decde04aa5aa97e224603d508483ba1a19e212db5d811910cba0c53a59df775b451f036ca86c1f8b94bad9bae62a8ef8e04260d41dd74f1c6f4d1c73f161ce990ae4186aa0583993544cbc6ed3ff04be64fe7c2b8f69454c3030f98912b20e57c906a34cd3389933259d1cdc60837267dab14593dfc4341433f7b16aa8ec901a66fc14f736ed45bc53517cde99db61d9011409851d7d1faeca234dbeb248f7caf54117157cbd99d17fc63a58a5404bb8e874139afea36e1e8f7eacb6c00a51f511624c1a3214b33b15acb27fd5de2c67854acc07097bc5f8385698b7d6659c0ff9e2c8e6c0ffa52005994251f9c0aea671d13e52542cfd02c4bef67f85271fa11b8462f907111209deec2686ec90671d2f3c96949f9a55deaee4d6d6d2b0ab95851b1d31a64c3001f7da42524622e9d8a8f3dfa1a3943b74b1ca6d5083ddef59879ba27a5d5e417ff461c26c368301edf8dc6be4ec64005a437dbbcca6c10d6be69fccc49b71b4f7d9db46942abe2f95816091279bda4e5ea0fdcab9fd581bd55ba03aa82e8116287b4672e44dc3a4aebdd40d88f225233902abf7e01cbee2a7796fbe59b6ba2eb3015349a95b426dd7e9a1954faefce00b4dc87a7ab903d15b44790779c8276689c06630db418614d492674b5d1065fc98a40be19c580033b24749603dfa93a95d2702cbc2acfc321485c4e540eeecf0b783c921696f362646b3d2d4cfe899ee873d361501e649937bb30fb720181ee789e7e43d7e868901'
NCAPPKEY = 'X82Y__966671c1369aefed2224839ab0a51809'
NCTOKENSTR = '5dd9ba8982c59ce2554335b859852bf2'
punish_url = f'https://s.taobao.com/search/_____tmd_____/slide?slidedata=%7B%22a%22%3A%22{NCAPPKEY}%22%2C%22t%22%3A%22{NCTOKENSTR}%22%2C%22n%22%3A%22{quote(encrypt_ua)}%22%2C%22p%22%3A%22%7B%5C%22ncSessionID%5C%22%3A%5C%22895d44109d5%5C%22%2C%5C%22umidToken%5C%22%3A%5C%22T2gACd0EVEtRabppKPSa9TxkMhhiL1LZbTmAdUgvRvEFaYl4NAFlWwJwkwx3gfMGJbQ%3D%5C%22%7D%22%2C%22scene%22%3A%22register%22%2C%22asyn%22%3A0%2C%22lang%22%3A%22cn%22%2C%22v%22%3A1039%7D&x5secdata={x5secdata}&v=08051974989157415'
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

res = requests.get(url=punish_url,headers=headers)
if res.json().get('code') == 0:
    logger.debug(res.json())
    x5sec = res.cookies.get_dict().get('x5sec')
    logger.success(f'SlideSuccess，x5sec：{x5sec}')