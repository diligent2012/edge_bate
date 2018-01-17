# coding=utf-8


import sys  
sys.path.append("..")
reload(sys)
sys.setdefaultencoding('utf-8')
import time
import string
import random
import MySQLdb
import json

import urllib
import urllib2
import json
import requests


def allow_send_time():
    Flag=True

    try:
        crawl_date_hour = time.strftime('%Y-%m-%d %H:00:00',time.localtime(time.time()))
        crawl_date_hour_start = time.strftime('%Y-%m-%d 00:00:00',time.localtime(time.time()))
        crawl_date_hour_end = time.strftime('%Y-%m-%d 07:00:00',time.localtime(time.time()))

        

        starttime=time.strptime(crawl_date_hour_start,'%Y-%m-%d %H:%M:%S')
        endtime=time.strptime(crawl_date_hour_end,'%Y-%m-%d %H:%M:%S')
        weibotime=time.strptime(str(crawl_date_hour),'%Y-%m-%d %H:%M:%S')

        if int(time.mktime(starttime))<= int(time.mktime(weibotime)) and int(time.mktime(endtime))>=int(time.mktime(weibotime)):
            Flag=False
        else:
            Flag=True

    except Exception as e:
        send_exception(traceback.format_exc())

    return Flag


def format_time(order_time):
    return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(order_time/1000))

def id_generator(size=17, chars=string.ascii_uppercase + string.digits):
    r_id = ''.join(random.choice(chars) for _ in range(size))
    return '888%s' % str(r_id)


def send_exception(exception_content):
    exception_content_format = json.dumps(exception_content.splitlines()).strip().replace('"','').replace("'",'')
    insert_id = insert_btc_binance_exception_log(exception_content_format)
    send_wechat("\nID:" + str(insert_id) + "\n" + str(exception_content_format))

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

# 插入 错误日志表
def insert_btc_binance_exception_log(exception_content):
    try:
        date = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        conn= MySQLdb.connect(
            host='127.0.0.1',
            port = 3306,
            user='omni_manage_pro',
            passwd='!omni123456manageMysql.pro',
            db ='z_omni_manage_pro',
        )
        cur = conn.cursor()
        cur.execute('set names utf8') #charset set code. it is not nessary now
        #sql = 'INSERT INTO omni_btc_binance_exception_log (`exception_content`,`date`) VALUES ("%s", "%s")' % (exception_content,date)
        sql = "INSERT INTO `omni_btc_binance_exception_log` (`exception_content`,`date`) VALUES ('%s', '%s')" % (exception_content,date)
        print sql
        cur.execute(sql)
        pk_id = conn.insert_id()
        conn.commit()
        return pk_id
        cur.close()
        conn.close()
    except Exception as e:
        print e
    return False