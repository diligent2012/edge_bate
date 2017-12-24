#!/usr/bin/python
#coding:utf-8
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


mailto_list = ['changaiqing@vip.163.com']
mail_host = 'smtp.163.com'
mail_user = 'omni_noreply@163.com'
mail_pass = 'omni163'
mail_subject = 'BTC 交易数据统计'
mail_content = ''

def send_mail(content):
    #content = "test" #get_send_content()
    msg = MIMEText(content,'html','utf-8')
    msg['Subject'] = mail_subject
    msg['From'] = "BTC Data Statistics" + "<" + mail_user + ">"
    msg['To'] = ";" . join(mailto_list)
    try:
        server = smtplib.SMTP()
        server.connect(mail_host)
        server.login(mail_user,mail_pass)
        print msg.as_string()
        server.sendmail(mail_user, mailto_list, msg.as_string())
        server.quit()
        print 'suc'

        return True
    except Exception, e:
        print str(e)
        return False


def crawl_enter_list():
    result={}
    header = {
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36',
        'Host': 'otcbtc.com',
    }
    response = requests.get('https://otcbtc.com/sell_offers?currency=eos&fiat_currency=cny&payment_type=all', headers=header, verify=False)
    if response.status_code != 200:
        return result

    try:
        soup = BeautifulSoup(response.text, "html.parser")
        info_list = soup.find('div',class_="current-rate")
        market_price = info_list.span.get_text().strip().split(' ')[0]
        date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
        crawl_date = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

        market_price_first = find_market(date)
        

        price_rate = (Decimal(market_price) - market_price_first) / market_price_first
        print price_rate
        price_rate_str = '%.2f%%' % (price_rate * 100)
        print price_rate_str
        content = "当天0点价格: " + str(market_price_first) + "; 当前价格: " + str(market_price) + "; 溢价率: " + price_rate_str
        if(price_rate * 100 >= 5):

            key_flag = str(market_price_first) + str(market_price) + price_rate_str
            is_send = find_send_refer(key_flag)
            if(is_send):
                content = "当天0点价格: " + str(market_price_first) + "; 当前价格: " + str(market_price) + "; 溢价率: " + price_rate_str
                print content
                send_mail(content)
                insert_send_refer(key_flag, date, crawl_date)
                send_wechat(str(market_price_first), str(market_price), price_rate_str)

        


    except Exception, e:
        print e.message


def find_market(date):
    try:
        conn= MySQLdb.connect(
            host='127.0.0.1',
            port = 3306,
            user='omni_btc',
            passwd='!omni123456btcMysql.pro',
            db ='z_omni_btc',
        )
        cur = conn.cursor()
        cur.execute('set names utf8') #charset set code. it is not nessary now
        sql = "SELECT market_price FROM `t_btc_market_price`  WHERE  date = '%s' order by crawl_date limit 1 " % (date)
        #sql = "INSERT INTO `ecs_t_marathon` (`name`, `start_run_time`) VALUES ('%s', '%s')" % (name, start_run_time)
        print sql
        cur.execute(sql)
        conn.commit()
        result = cur.fetchone()
        return result[0]
        
        cur.close()
        conn.close()
    except Exception, e:
        print e.message
    return False


def insert_data(market_price, date, crawl_date):
    try:
        conn= MySQLdb.connect(
            host='127.0.0.1',
            port = 3306,
            user='omni_btc',
            passwd='!omni123456btcMysql.pro',
            db ='z_omni_btc',
        )
        cur = conn.cursor()
        cur.execute('set names utf8') #charset set code. it is not nessary now
        sql = "INSERT INTO `t_btc_market_price` (`market_price`, `date`, `crawl_date`) VALUES ('%s',  '%s', '%s')" % (market_price, date, crawl_date)
        #sql = "INSERT INTO `ecs_t_marathon` (`name`, `start_run_time`) VALUES ('%s', '%s')" % (name, start_run_time)
        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
    except Exception, e:
        print e.message


def insert_send_refer(flag, date, crawl_date):
    try:
        conn= MySQLdb.connect(
            host='127.0.0.1',
            port = 3306,
            user='omni_btc',
            passwd='!omni123456btcMysql.pro',
            db ='z_omni_btc',
        )
        cur = conn.cursor()
        cur.execute('set names utf8') #charset set code. it is not nessary now
        sql = "INSERT INTO `t_btc_send_refer` (`flag`, `date`, `crawl_date`) VALUES ('%s', '%s', '%s')" % (flag, date, crawl_date)
        #sql = "INSERT INTO `ecs_t_marathon` (`name`, `start_run_time`) VALUES ('%s', '%s')" % (name, start_run_time)
        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
    except Exception, e:
        print e.message

def find_send_refer(flag):
    try:
        conn= MySQLdb.connect(
            host='127.0.0.1',
            port = 3306,
            user='omni_btc',
            passwd='!omni123456btcMysql.pro',
            db ='z_omni_btc',
        )
        cur = conn.cursor()
        cur.execute('set names utf8') #charset set code. it is not nessary now
        sql = "SELECT count(*) as send_count FROM `t_btc_send_refer`  WHERE flag = '%s' " % (flag)
        #sql = "INSERT INTO `ecs_t_marathon` (`name`, `start_run_time`) VALUES ('%s', '%s')" % (name, start_run_time)
        print sql
        cur.execute(sql)
        conn.commit()
        result = cur.fetchone()
        if result[0] >= 3:
            return False
        else:
            return True
        
        cur.close()
        conn.close()
    except Exception, e:
        print e.message
    return True

def send_wechat(market_price_first, market_price, price_rate_str):
    post_url = 'https://www.datasource.top/api/portal/btc/send'
    
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
    }

    p_data = {
        'market_price_first':market_price_first,
        'market_price':market_price,
        'price_rate_str':price_rate_str
    }
    data_u = urllib.urlencode(p_data)
    resp = requests.post(post_url, data=data_u, headers=headers)
    print resp.content
    return resp.content

def crawl_start():
    print "start : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    crawl_enter_list()
    #send_wechat()


def main():
    crawl_start();

if __name__ == '__main__':
    main()