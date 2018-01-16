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
from db import * 


user_agent_list = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)",
    "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11"
]


def get_github_eos_code_tags():
    result={}
    header = {
    }
    header['User-Agent'] = random.sample(user_agent_list, 1)
    url = 'https://github.com/EOSIO/eos/tags'
    response = requests.get(url, headers=header, verify=False, allow_redirects=False)
    if response.status_code != 200:
        return result

    try:
        soup = BeautifulSoup(response.text, "html.parser")
        info_list = soup.find('table',class_="releases-tag-list").find_all('tr')
        
        for key,item in enumerate(info_list):
            tag = item.find('span',class_="tag-name").get_text().strip()
            date = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
            is_tag = find_btc_eos_github_code_tag(tag)
            if (not is_tag):
                content = get_send_content(tag)
                send_wechat(content)
            insert_btc_eos_github_code_tag(tag, date)
    except Exception, e:
        print e.message

    return 0

def get_send_content(tag):
    content = "\nGitHub EOS 代码发布" + "新的Tag为: " + tag  
    return content

#入口
def start():
    print "start : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    get_github_eos_code_tags()
    print "end : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

    

def main():
    start();

if __name__ == '__main__':
    main()