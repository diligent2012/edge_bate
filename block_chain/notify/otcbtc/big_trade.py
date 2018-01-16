#!/usr/bin/python
#coding:utf-8
# OTCBTC 
# 市场价格、最近成交价格、 当前卖出价格、当前买入价格

import sys,os
# sys.path.append("../../platform/")
sys.path.append("../../common/otcbtc")
sys.path.append("../../common")
reload(sys)
sys.setdefaultencoding('utf-8')

import sys  
import sqlite3
import requests
import json
from bs4 import BeautifulSoup
import re
from datetime import datetime
from datetime import timedelta
import MySQLdb
import time

import smtplib
from email.mime.text import MIMEText
from email.header import Header


import urllib
import urllib2
import json
import requests

import random
import re

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)



from global_setting import *
from util import *
from db import * 


user_agent_list = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)",
    "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11"
]


def get_trade_record():

    result={}
    header = {
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36',
        'Host': 'otcbtc.com',
    }
    response = requests.get('https://otcbtc.com/', headers=header, verify=False)
    if response.status_code != 200:
        return result

    try:
        soup = BeautifulSoup(response.text, "html.parser")
        info_list = soup.find_all('div',class_="lp-section-2-coin")#.find_all('div',class_="container").find_all('div',class_="row").find_all('div',class_="col-md-4")
        # date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
        # crawl_date = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        detail_info =  info_list[1].find('div',class_="container").find('div',class_="row").find_all('div',class_="col-md-4")
        
        date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
        crawl_date = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        crawl_date_hour = time.strftime('%Y-%m-%d %H:00:00',time.localtime(time.time()))

        for key,item in enumerate(detail_info):
            for content in  item.find_all('tr'):
                trade_duration = ' '.join(content.span.text.strip().split())
                content.span.extract()
                content.span.extract()
                trade_content = ' '.join(content.text.split())
                content_list = trade_content.split(' ')
                
                duration_list = trade_duration.replace('(','').replace(')','').split(' ')
                
                trade_num = content_list[2]
                trade_symbol = content_list[3]
                trade_duration = duration_list[0]

                trade_pk_key = trade_content + " " + trade_duration

                # 多少分钟之内不能重复
                crawl_date_refer = (datetime.now() - timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")

                is_crawl = find_otcbtc_trade_record_refer(trade_pk_key, crawl_date_refer)
                if(is_crawl):
                    insert_otcbtc_trade_record(trade_num, trade_symbol, trade_duration, date, crawl_date, crawl_date_hour)
                    insert_otcbtc_trade_record_refer(trade_pk_key, crawl_date)

                if(float(trade_num) > 999 and 'EOS' == trade_symbol):
                    content = get_send_content(trade_symbol, trade_num)
                    send_wechat(content)
                

    except Exception as e:
        print e
    return False


def get_send_content(symbol, num):
    content = "\nOTCBTC 有大交易发生" + "币种: " + symbol + " 数量: " + str(num)
    return content

#入口
def start():
    print "start : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    get_trade_record()
    print "end : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

def main():
    start();

if __name__ == '__main__':
    main()