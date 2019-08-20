#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: 罗兴红
@contact: EX-LUOXINGHONG001@pingan.com.cn
@file: test.py
@time: 2019/8/20 9:46
@desc:
'''

data = (3, '转发微博。', 1703513474, '微博 weibo.com', 'https://m.weibo.cn/status/6bcduN?mblogid=6bcduN&luicode=10000011&lfid=1076031703513474', '转发微博。', '天使投资人', 1, '未引用图片', '2010-11-23', '221101123773491920', 0)

sql = "insert into sina_weibos(reposts_count,text,uid,source,thumbnail,raw_text,nickname,comments_count,pictures,created_at,weibo_id,attitudes_count) value(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"


print(sql%(data))