# -*- coding: utf-8 -*-
BOT_NAME = 'SinaWeibo'
SPIDER_MODULES = ['SinaWeibo.spiders']
NEWSPIDER_MODULE = 'SinaWeibo.spiders'
ROBOTSTXT_OBEY = False
COOKIES_ENABLED = False

# 定义scraoy日志的目录，等级，名字
import datetime
to_day = datetime.datetime.now()
log_file_path = "./logs/{}_{}_{}.log".format(to_day.year, to_day.month, to_day.day)
LOG_LEVEL = "INFO"
LOG_FILE = log_file_path

RANDOM_UA_TYPE = 'random'

COOKIES_URL = 'http://106.12.8.109:5005/weibo/random'
PROXY_URL = 'http://106.12.8.109:5010/get/'

# 增加爬虫速度及防ban配置
DOWNLOAD_DELAY = 0.25
DOWNLOAD_FAIL_ON_DATALOSS = False
CONCURRENT_REQUESTS = 1
CONCURRENT_REQUESTS_PER_DOMAIN = 1
CONCURRENT_REQUESTS_PER_IP = 1
DOWNLOAD_TIMEOUT = 60


DOWNLOADER_MIDDLEWARES = {
    'SinaWeibo.middlewares.RandomUserAgentMiddleware': 300,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'SinaWeibo.middlewares.CookiesMiddleware': 310,
    # 'SinaWeibo.middlewares.ProxyMiddleware': 320,
}

ITEM_PIPELINES = {
    'SinaWeibo.pipelines.SinaweiboPipeline': 310,
    'SinaWeibo.pipelines.CleanTimePipeline': 315,
    'SinaWeibo.pipelines.Fanscount_2_int': 316,
    'SinaWeibo.pipelines.MysqlTwistedPipline': 325,

}


KEYWORD = '天使投资人'


MYSQL_HOST = 'localhost'
MYSQL_PORT = 3306
MYSQL_DBNAME = "weibo"
MYSQL_USER = 'root'
MYSQL_PASSWD = 'lxh123'
MYSQL_CHARSET = "utf8mb4"


# 设置最大等待时间、失败重试次数
#默认响应时间是180s，长时间不释放会占用一个并发量影响效率
DOWNLOAD_TIMEOUT = 10
# 是否进行失败重试
RETRY_ENABLED = True
# 失败重试的次数，连续失败3次后会抛出TimeOut异常被errback捕获
RETRY_TIMES = 3