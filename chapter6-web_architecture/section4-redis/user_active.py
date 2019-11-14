# coding=utf-8
import time
import random
from datetime import datetime

import redis
# 通过位图计算用户登录情况  01010100000001 (1表示用户登录)
r = redis.StrictRedis(host='localhost', port=6379, db=0)
ACCOUNT_ACTIVE_KEY = 'account:active'

# 为了测试方便，每次启动后先清理Redis
r.flushall()
now = datetime.utcnow()


def record_active(account_id, t=None):
    if t is None:
        t = datetime.utcnow()
    p = r.pipeline()  # 使用Redis提供的事务
    key = ACCOUNT_ACTIVE_KEY
    for arg in ('year', 'month', 'day'):
        key = '{}:{}'.format(key, getattr(t, arg))
        p.setbit(key, account_id, 1)  # 设置年、月、日三种键
    p.execute()  # 事务提交


def gen_records(max_days, population, k):  # 随机生成一些数据
    for day in range(1, max_days):  # 日期需要从1开始
        time_ = datetime(now.year, now.month, day)
        accounts = random.sample(range(population), k)
        for account_id in accounts:
            record_active(account_id, time_)


def calc_memory():
    r.flushall()

    print 'USED_MEMORY: {}'.format(r.info()['used_memory_human'])

    start = time.time()

    gen_records(21, 1000000, 100000)

    print 'COST: {}'.format(time.time() - start)
    print 'USED_MEMORY: {}'.format(r.info()['used_memory_human'])


# 最后会添加从1号到28号的数据，每天都从10,000个用户中随机选2000个用户登录
gen_records(29, 10000, 2000)

print r.bitcount('{}:{}:{}'.format(ACCOUNT_ACTIVE_KEY, now.year, now.month))
print r.bitcount('{}:{}:{}:{}'.format(ACCOUNT_ACTIVE_KEY, now.year,
                                      now.month, now.day))

account_id = 1200
print r.getbit('{}:{}:{}'.format(ACCOUNT_ACTIVE_KEY, now.year, now.month),
               account_id)

print r.getbit('{}:{}:{}'.format(ACCOUNT_ACTIVE_KEY, now.year, now.month),
               10001)

keys = ['{}:{}:{}:{}'.format(ACCOUNT_ACTIVE_KEY, now.year, now.month, day)
        for day in range(1, 3)]
r.bitop('or', 'destkey:or', *keys)
print r.bitcount('destkey:or')

r.bitop('and', 'destkey:and', *keys)
print r.bitcount('destkey:and')
