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
from decimal import *

import urllib
import urllib2
import json
import requests

import random

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)



from global_setting import *
from util import *


user_agent_list = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)",
    "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11"
]


def get_trade_sell_price():
    result={}
    header = {
    }
    header['User-Agent'] = random.sample(user_agent_list, 1)
    url = 'https://github.com/EOSIO/eos/tree/eos-noon'
    response = requests.get(url, headers=header, verify=False, allow_redirects=False)
    if response.status_code != 200:
        return result

    try:
        soup = BeautifulSoup(response.text, "html.parser")
        info_list = soup.find('ul',class_="pagehead-actions").find_all('li')
        print "Watch(查看): " + info_list[0].find('a',class_="social-count").get_text().strip().replace(',','')
        print "Star(点赞): " + info_list[1].find('a',class_="social-count").get_text().strip().replace(',','')
        print "Fork(收藏): " + info_list[2].find('a',class_="social-count").get_text().strip().replace(',','')

        info_list_branch = soup.find('ul',class_="numbers-summary").find_all('li')
        
        print "commits(提交): " + info_list_branch[0].find('span',class_="num").get_text().strip().replace(',','')
        print "branches(分支): " + info_list_branch[1].find('span',class_="num").get_text().strip().replace(',','')
        print "releases(发布): " + info_list_branch[2].find('span',class_="num").get_text().strip().replace(',','')
        print "contributors(贡献者): " + info_list_branch[3].find('span',class_="num").get_text().strip().replace(',','')
        


    except Exception, e:
        print e.message

    return 0


#入口
def start():
    print "start : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    get_trade_sell_price()
   
    print "end : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))


def main():
    start();

if __name__ == '__main__':
    main()