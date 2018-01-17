# coding=utf-8


import sys  
sys.path.append("..")
import time
import string
import random


import urllib
import urllib2
import json
import requests

def allow_send_time():
    crawl_date_hour = time.strftime('%Y-%m-%d %H:00:00',time.localtime(time.time()))
    crawl_date_hour_start = time.strftime('%Y-%m-%d 00:00:00',time.localtime(time.time()))
    crawl_date_hour_end = time.strftime('%Y-%m-%d 07:00:00',time.localtime(time.time()))

    Flag=True

    starttime=time.strptime(crawl_date_hour_start,'%Y-%m-%d %H:%M:%S')
    endtime=time.strptime(crawl_date_hour_end,'%Y-%m-%d %H:%M:%S')
    weibotime=time.strptime(str(crawl_date_hour),'%Y-%m-%d %H:%M:%S')

    if int(time.mktime(starttime))<= int(time.mktime(weibotime)) and int(time.mktime(endtime))>=int(time.mktime(weibotime)):
        Flag=False
    else:
        Flag=True

    return Flag


def format_time(order_time):
    return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(order_time/1000))

def id_generator(size=17, chars=string.ascii_uppercase + string.digits):
    r_id = ''.join(random.choice(chars) for _ in range(size))
    return '888%s' % str(r_id)

# 发送微信通知
def send_wechat(content):
    post_url = 'https://www.datasource.top/api/portal/btc/send'
    
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
    }

    p_data = {
        'content':content
    }
    data_u = urllib.urlencode(p_data)
    resp = requests.post(post_url, data=data_u, headers=headers)