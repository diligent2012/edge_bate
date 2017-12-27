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

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


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

        
        span_list = info_list.find_all('span')

        online_number = span_list[0].get_text().strip().split(' ')[0].replace(',','')
        market_price = span_list[1].get_text().strip().split(' ')[0]

        #market_price = info_list.span.get_text().strip().split(' ')[0]

        #print market_price
        date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
        crawl_date = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        crawl_date_hour = time.strftime('%Y-%m-%d %H:00:00',time.localtime(time.time()))


        insert_data(market_price, online_number, date, crawl_date, crawl_date_hour)
        # market_price_first = find_market(date)

        # price_rate = (Decimal(market_price) - market_price_first) / market_price_first
        # print price_rate
        # price_rate_str = '%.2f%%' % (price_rate * 100)
        # print price_rate_str
        # content = "当天0点价格: " + str(market_price_first) + "; 当前价格: " + str(market_price) + "; 溢价率: " + price_rate_str
        # if(price_rate * 100 >= 5):

        #     key_flag = str(market_price_first) + str(market_price) + price_rate_str
        #     is_send = find_send_refer(key_flag)
        #     if(is_send):
        #         content = "当天0点价格: " + str(market_price_first) + "; 当前价格: " + str(market_price) + "; 溢价率: " + price_rate_str
        #         print content
        #         send_mail(content)
        #         insert_send_refer(key_flag, date, crawl_date)
        #         send_wechat(str(market_price_first), str(market_price), price_rate_str)

        


    except Exception, e:
        print e.message

def insert_data(market_price, online_number, date, crawl_date, date_hour):
    try:
        conn= MySQLdb.connect(
            host='127.0.0.1',
            port = 3306,
            user='omni_manage_pro',
            passwd='!omni123456manageMysql.pro',
            db ='z_omni_manage_pro',
        )
        cur = conn.cursor()
        cur.execute('set names utf8') #charset set code. it is not nessary now
        sql = "INSERT INTO `omni_btc_market_price` (`market_price`, `online_number`, `date`, `crawl_date`, `date_hour`) VALUES ('%s',  '%s', '%s', '%s', '%s')" % (market_price, online_number, date, crawl_date, date_hour)
        print sql
        #sql = "INSERT INTO `ecs_t_marathon` (`name`, `start_run_time`) VALUES ('%s', '%s')" % (name, start_run_time)
        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
    except Exception, e:
        print e.message



def crawl_start():
    print "start : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    crawl_enter_list()
    #send_wechat()


def main():
    crawl_start();

if __name__ == '__main__':
    main()