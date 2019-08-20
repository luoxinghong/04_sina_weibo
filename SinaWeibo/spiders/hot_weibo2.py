# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
import re
import copy
import requests
from lxml import etree
import logging
import json
import time
from fake_useragent import UserAgent
import glob

logger = logging.getLogger(__name__)



class HotWeibo2Spider(scrapy.Spider):
    name = 'hot_weibo2'
    allowed_domains = ['m.weibo.cn']
    start_urls = ['http://m.weibo.cn/']

    page_url = 'https://m.weibo.cn/api/container/getIndex?containerid=102803&openApp=0&page={}'
    first_comment_url = 'https://m.weibo.cn/comments/hotflow?id={}&mid={}&max_id_type=0'
    first_comment_url2 = 'https://m.weibo.cn/comments/hotflow?id={}&mid={}&max_id={}&max_id_type=0'

    def get_headers(self):
        headers = {
            'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0',
            'Host': 'm.weibo.cn',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://m.weibo.cn/status/Hqu2g56w0',
            'DNT': '1',
            'Connection': 'keep-alive',
        }
        cookie_str = ""
        json_cookie = requests.get("http://127.0.0.1:5005/weibo/random").text
        for key, value in json.loads(json_cookie).items():
            str_temp = key + '=' + value + ";"
            cookie_str += str_temp
        headers["Cookie"] = cookie_str
        ua = UserAgent()
        headers["User-agent"] = ua.random
        return headers

    # 获取热门微博列表
    def parse(self, response):
        for page in range(1, 30):
            headers = self.get_headers()
            page_url = 'https://m.weibo.cn/api/container/getIndex?containerid=102803&openApp=0&page={}'
            try:
                response = requests.get(url=page_url.format(page), headers=headers).text
                weibo_info_list = json.loads(response)['data']['cards']
            except Exception as e:
                print(response)
                continue

            for card in weibo_info_list:
                headers = self.get_headers()
                weibo_json = {
                    'weibo': None,
                    'data': None
                }
                first_comment_json_list = []

                if 'card_group' in card:
                    mblog = card['card_group'][0]['mblog']
                else:
                    mblog = card['mblog']
                # 获取作者和内容
                wauthor = mblog['user']['screen_name']
                wb_id = mblog['id']
                print("①微博wb_id", wb_id)

                wbid_list = [i.replace("\n", "") for i in open("weibo_id.txt").readlines()]

                if wb_id not in wbid_list:
                    # 判断isLongText，True需要单独加载，false在当前页面获取
                    if mblog['isLongText']:
                        # 获取微博id,拼接出微博路由
                        try:
                            detail_weibo_url = 'https://m.weibo.cn/statuses/extend?id={}'.format(wb_id)
                            response2 = requests.get(url=detail_weibo_url, headers=headers)
                            detail_weibo = json.loads(response2.text)['data']['longTextContent']
                            etree2 = etree.HTML(detail_weibo)
                            wcontent = ''.join(etree2.xpath('//*/text()'))
                        except Exception as e:
                            logger.info("加载微博长内容失败：" + detail_weibo_url)
                            logger.info(response2.text)
                    else:
                        etree2 = etree.HTML(mblog['text'])
                        wcontent = ''.join(etree2.xpath('//*/text()'))
                    # 拼接完整的微博内容
                    weibo_content = wauthor + ': ' + wcontent
                    weibo_json['weibo'] = weibo_content
                    print("微博内容：", weibo_content)

                    first_comment_url = 'https://m.weibo.cn/comments/hotflow?id={}&mid={}&max_id_type=0'
                    first_comment_url2 = 'https://m.weibo.cn/comments/hotflow?id={}&mid={}&max_id={}&max_id_type=0'
                    first_comment_json_list = []
                    # 获取一级评论
                    for page_number in range(1, 3000):
                        time.sleep(1)
                        if page_number == 1:
                            first_comment_url = first_comment_url.format(wb_id, wb_id)
                        else:
                            first_comment_url = first_comment_url2.format(wb_id, wb_id, fmax_id)
                        print("③first_comment_page_url：", first_comment_url)

                        response3 = requests.get(first_comment_url, headers=headers).text
                        try:
                            fdata = json.loads(response3)
                        except Exception as e:
                            print(e)
                            break

                        # 如果一级评论页访问异常或者无data内容，退出
                        if 'data' not in fdata:
                            break

                        first_comment_data = fdata['data']
                        # 获取一级评论下一页的fmax_id
                        fmax_id = first_comment_data['max_id']
                        print("④fmax_id：", fmax_id)
                        first_comment_list = first_comment_data['data']

                        # 遍历一级评论
                        for first_comment in first_comment_list:
                            root_id = first_comment['rootid']
                            fauthor = first_comment['user']['screen_name']
                            fcontent = ''.join(etree.HTML(first_comment['text']).xpath('//*/text()'))
                            first_comment_content = fauthor + ': ' + fcontent
                            first_comment_json = {
                                'first_comment': None,
                                'data': []
                            }
                            first_comment_json['first_comment'] = first_comment_content
                            # 一级评论内容
                            print("======first_comment_content：", first_comment_content)

                            # 获取二级评论总数
                            second_comment_status = first_comment['total_number']
                            print("second_comment_status:", second_comment_status)

                            # 遍历二级评论
                            if second_comment_status != 0:
                                second_comment_json_list = []
                                second_comment_count = 0
                                smax_id = None
                                for page_number in range(1, 100):
                                    before_smax_id = None
                                    current_smax_id = None
                                    if page_number == 1:
                                        second_comment_url = 'https://m.weibo.cn/comments/hotFlowChild?cid={}&max_id=0&max_id_type=0'.format(
                                            root_id)
                                    else:
                                        second_comment_url = 'https://m.weibo.cn/comments/hotFlowChild?cid={}&max_id={}&max_id_type=0'.format(
                                            root_id, smax_id)
                                    print("--second_comment_url：", second_comment_url)
                                    response4 = requests.get(url=second_comment_url, headers=headers)
                                    try:
                                        second_comment_data = json.loads(response4.text)
                                    except Exception as e:
                                        headers = self.get_headers()
                                        print(e)
                                        break
                                    if 'max_id' not in second_comment_data:
                                        break
                                    smax_id = second_comment_data['max_id']
                                    current_smax_id = smax_id
                                    if current_smax_id == before_smax_id:
                                        break
                                    else:
                                        before_smax_id = current_smax_id
                                    second_comment_list = second_comment_data['data']

                                    for second_comment in second_comment_list:
                                        sauthor = second_comment['user']['screen_name']
                                        etree4 = etree.HTML(second_comment['text'])
                                        scontent = ''.join(etree4.xpath('//*/text()'))
                                        second_comment_content = sauthor + ': ' + scontent
                                        created_at = second_comment["created_at"]
                                        second_comment_content = {"created_at": created_at,
                                                                  "second_comment": second_comment_content}
                                        second_comment_json_list.append(second_comment_content)
                                        second_comment_count += 1
                                        print("第{}条second_comment：".format(second_comment_count), scontent)
                                    if smax_id == 0 or second_comment_data["ok"] == 0:
                                        break

                                first_comment_json['data'] = second_comment_json_list

                            first_comment_json_list.append(first_comment_json)

                        if int(fmax_id) == 0:
                            break
                    weibo_json['data'] = first_comment_json_list

                    with open("weibo_id.txt", "a", encoding='utf-8') as g:
                        g.write(wb_id + "\n")
                        g.close()

                    if first_comment_json_list != [] and len(json.dumps(weibo_json)) > 12000:
                        total_file_number = glob.glob(pathname='./data/*.json')
                        file_id = len(total_file_number)
                        with open("contentes.txt", "a", encoding='utf-8') as gg:
                            gg.write(weibo_content + "\n")
                            gg.write("*" * 50 + "\n")
                            gg.close()
                        with open('data/{:0>6}.json'.format(file_id), 'w', encoding='utf-8') as f:
                            f.write(json.dumps(weibo_json))
                            f.close()