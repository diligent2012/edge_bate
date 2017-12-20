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


def crawl_enter_list():
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
        info_list = soup.find_all('div',class_="col-md-12 text-center")
        date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
        crawl_date = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        print info_list
        all_info = []
        for key,item in enumerate(info_list):
            for key_c, content in enumerate(item.find_all('tr')):
                if(key_c > 0):

                    item_0 = {}
                    currency = content.find_all('td')[0].text.strip()
                    item_0['currency'] = currency
                    item_0['bourse'] = "CoinMarketcap"
                    item_0['price'] = content.find_all('td')[1].text.strip().split(" ")[0]   
                    all_info.append(item_0)

                    item_1 = {}
                    item_1['currency'] = currency
                    item_1['bourse'] = "Bitfinex"
                    item_1['price'] = content.find_all('td')[2].text.strip().split(" ")[0]   
                    all_info.append(item_1)

                    item_2 = {}
                    item_2['currency'] = currency
                    item_2['bourse'] = "Bitstamp"
                    item_2['price'] = content.find_all('td')[3].text.strip().split(" ")[0]   
                    all_info.append(item_2)

           
        for info in all_info:
            date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
            crawl_date = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
            price = 0
            if(info['price'] == 'N/A'):
                price = 0
            else:
                price = info['price']
            insert_data(info['currency'], price, info['bourse'], date, crawl_date) 


    except Exception, e:
        print e.message


def insert_data(currency, price, bourse, date, crawl_date):
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
        sql = "INSERT INTO `t_btc_price` (`currency`, `price`, `bourse`, `date`, `crawl_date`) VALUES ('%s', '%s', '%s', '%s', '%s')" % (currency, price, bourse, date, crawl_date)
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

def main():
    crawl_start();

if __name__ == '__main__':
    main()