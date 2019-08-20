# -*- coding: utf-8 -*-
from scrapy import Item,Field



class Useritem(Item):
    table_name = 'users'
    #用户唯一id
    uid = Field()
    #用户名
    name = Field()
    #用户头像
    cover = Field()
    #微博描述
    description = Field()
    #粉丝数
    follows_count = Field()
    #关注数
    fans_count = Field()
    #用户微博类表
    weibo_url = Field()


class Weiboitem(Item):
    table_name ='weibos'
    #用户唯一id
    uid = Field()
    #用户昵称
    nickname = Field()
    #转发数
    reposts_count = Field()
    #评论数
    comments_count = Field()
    #点赞数
    attitudes_count = Field()
    #微博正文
    text = Field()
    #转发时的微博正文
    raw_text = Field()
    #微博配图
    pictures = Field()      #pics large url
    #发布平台 eg：小米9
    source = Field()
    #微博原网页
    thumbnail = Field()
    #微博创建时间
    created_at = Field()
    #微博的唯一id，用于去重
    weibo_id = Field()


class HotWeiBoitem(Item):
    table_name ='hot_weibo'
    #用户唯一id
    wb_id = Field()
    #微博作者
    author = Field()
    # 微博内容
    content = Field()


