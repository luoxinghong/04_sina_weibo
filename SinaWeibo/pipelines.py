# -*- coding: utf-8 -*-
from SinaWeibo.items import Weiboitem, Useritem
import time
import re
import json
import pymysql
from twisted.enterprise import adbapi
from pymysql import cursors

import logging
logger = logging.getLogger(__name__)


class SinaweiboPipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, Weiboitem):
            if item.get('pictures'):
                pictures = [pic.get('url') for pic in item['pictures']]
                item['pictures'] = json.dumps(pictures)
            else:
                item['pictures'] = '未引用图片'
        return item


class CleanTimePipeline():
    def parse_time(self, date):
        if re.match('刚刚', date):
            date = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
        if re.match('\d+分钟前', date):
            minute = re.match('(\d+)', date).group(1)
            date = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time() - float(minute) * 60))
        if re.match('\d+小时前', date):
            hour = re.match('(\d+)', date).group(1)
            date = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time() - float(hour) * 60 * 60))
        if re.match('昨天.*', date):
            date = re.match('昨天(.*)', date).group(1).strip()
            date = time.strftime('%Y-%m-%d', time.localtime(time.time() - 24 * 60 * 60)) + ' ' + date
        if re.match('\d{2}-\d{2}', date):
            date = time.strftime('%Y-', time.localtime()) + date
        return date

    def process_item(self, item, spider):
        created_time = item.get('created_at')
        # 发布时间可能为空，防止出现  KeyError: 'created_at'
        if created_time:
            item['created_at'] = self.parse_time(created_time)
        return item


class Fanscount_2_int():
    # 将粉丝数转换为int类型

    def parse_number(self, date):
        # if re.match('\d+', date):
        #     date = int(date)
        if re.match('\d+万', date):
            date = int(re.match('(\d+)', date).group(1)) * 10000
        elif re.match('\d+亿', date):
            date = int(re.match('(\d+)', date).group(1)) * 100000000
        elif re.match('\d+', date):
            date = int(date)
        return int(date)

    def process_item(self, item, spider):
        fans_count = item.get('fans_count')
        if fans_count:
            item['fans_count'] = self.parse_number(str(fans_count))
        return item


class MysqlTwistedPipline(object):
    def __init__(self, pool):
        self.dbpool = pool

    @classmethod
    def from_settings(cls, settings):
        params = dict(
            host=settings['MYSQL_HOST'],
            port=settings['MYSQL_PORT'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            charset=settings['MYSQL_CHARSET'],
            cursorclass=pymysql.cursors.DictCursor
        )
        db_pool = adbapi.ConnectionPool('pymysql', **params)
        return cls(db_pool)

    def process_item(self, item, spider):
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider)

    def handle_error(self, failure, item, spider):
        # 处理异步插入的异常
        logger.warning("数据库插入异常===" + str(failure))

    def do_insert(self, cursor, item):
        # 执行具体的插入
        # 根据不同的item 构建不同的sql语句并插入到mysql中
        data = dict(item)
        keys = ','.join(data.keys())
        values = ','.join(['%s'] * len(data))
        sql = 'insert into %s(%s) value(%s)' % (item.table_name, keys, values)
        cursor.execute(sql, tuple(data.values()))
    def close_spider(self, spider):
        self.dbpool.close()
