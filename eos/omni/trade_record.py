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
        info_list = soup.find_all('div',class_="col-md-4")
        date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
        crawl_date = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        crawl_date_hour = time.strftime('%Y-%m-%d %H:00:00',time.localtime(time.time()))

        for key,item in enumerate(info_list):
            if(key < 3):
                for content in item.find_all('td'):
                    
                    imp_content = content.text.split('(')[0]
                    miao = content.text.split('(')[1].split(' ')[0]

                    count_clutter = imp_content.split('=>')[1].strip()

                    count = count_clutter.split(' ')[0].strip()
                    currency = count_clutter.split(' ')[1].strip()
                    print count + "" + currency
                    count_flag = count + currency +  miao
                    is_crawl = find_record_refer(count_flag)
                    if(is_crawl):
                        insert_data('otcbtc', count, currency, date, crawl_date_hour, crawl_date)
                        insert_record_refer(count_flag, crawl_date)

    except Exception, e:
        print e.message


def insert_data(platform, quantity, currency, date, date_hour, crawl_date):
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
        sql = "INSERT INTO `omni_btc_trade_record` (`platform`, `quantity`, `currency`, `date`, `date_hour`, `crawl_date`) VALUES ('%s', '%s', '%s', '%s', '%s', '%s')" % (platform, quantity, currency, date, date_hour, crawl_date)
        #sql = "INSERT INTO `ecs_t_marathon` (`name`, `start_run_time`) VALUES ('%s', '%s')" % (name, start_run_time)
        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
    except Exception, e:
        print e.message

def insert_record_refer(flag, date):
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
        sql = "INSERT INTO `omni_btc_trade_record_refer` (`flag`, `date`) VALUES ('%s', '%s')" % (flag, date)
        #sql = "INSERT INTO `ecs_t_marathon` (`name`, `start_run_time`) VALUES ('%s', '%s')" % (name, start_run_time)
        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
    except Exception, e:
        print e.message

def find_record_refer(flag):
    try:
        conn= MySQLdb.connect(
            host='127.0.0.1',
            port = 3306,
            user='omni_manage_pro',
            passwd='!omni123456manageMysql.pro',
            db ='z_omni_manage_pro',
        )
        cur = conn.cursor()
        crawl_date_refer = (datetime.now() - timedelta(minutes=3)).strftime("%Y-%m-%d %H:%M:%S")
        cur.execute('set names utf8') #charset set code. it is not nessary now
        sql = "SELECT * FROM `omni_btc_trade_record_refer`  WHERE flag = '%s' and date >= '%s' " % (flag, crawl_date_refer)
        #sql = "INSERT INTO `ecs_t_marathon` (`name`, `start_run_time`) VALUES ('%s', '%s')" % (name, start_run_time)
        cur.execute(sql)
        conn.commit()
        result = cur.fetchall()
        if result:
            return False
        else:
            return True
        
        cur.close()
        conn.close()
    except Exception, e:
        print e.message
    return True

def crawl_start():
    print "start : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    crawl_enter_list()

def main():
    crawl_start();

if __name__ == '__main__':
    main()