# -*- coding: utf-8 -*-
import random
from redis import StrictRedis, ConnectionPool

# Redis 数据库链接
REDIS_URL = 'redis://127.0.0.1:6379/10'


class RedisClient(object):

    def __init__(self, key, v):
        """
        初始化 Redis 数据库, 存储易盾各个站点的 wm_did
        """
        self.db = StrictRedis(host='localhost',port=6379,db=10,password='')
        # 存储字段名: 该系统仅存储指纹和 wm_did
        self.key = key
        # 版本, 指纹: 2.13.2, wm_did: v
        self.v = v

    def name(self):
        """
        获取 Hash 的名称
        :return: Hash 名称
        """
        return "{key}:{v}".format(key=self.key, v=self.v)

    def set(self, site, value):
        """
        设置键值对
        :param site: 站点名
        :param value: 字段值
        :return:
        """
        return self.db.hset(self.name(), site, value)

    def expire(self, time):
        """
        设置过期时间
        :param time: 过期时间, 单位 s
        :return:
        """
        self.db.expire(self.name(), time)

    def get(self, site):
        """
        根据键名获取键值
        :param site: 站点名
        :return:
        """
        return self.db.hget(self.name(), site)

    def delete(self, site):
        """
        根据键名删除键值对
        :param site: 站点名
        :return: 删除结果
        """
        return self.db.hdel(self.name(), site)

    def count(self):
        """
        获取数目
        :return: 数目
        """
        return self.db.hlen(self.name())

    def random(self):
        """
        随机得到键值
        :return: 随机 Cookies
        """
        return random.choice(self.db.hvals(self.name()))

    def sites(self):
        """
        获取该字段的所有站点值
        :return: 所有站点
        """
        return self.db.hkeys(self.name())

    def all(self):
        """
        获取所有键值对
        :return: 站点与 wm_did 的映射表
        """
        return self.db.hgetall(self.name())
