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



def start_monitor():
    date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    #卖出价格(出售)
    min_sell =  find_min_sell(date)

    # 成本价格(收购)
    min_buy =  find_min_buy(date)
    #print Decimal(min_sell)
    #print (Decimal(min_sell) - (Decimal(min_sell+min_buy) * Decimal(0.005))) 
    entry_money_rate = (Decimal(min_sell) - Decimal(min_sell+min_buy) * Decimal(0.005)) / Decimal(min_buy) 
    entry_money_rate_str = '%.2f%%' % (entry_money_rate * 100)
    if( entry_money_rate * 100 > 104):
        content = "卖出价格(出售): " + str(min_sell) + "; 成本价格(收购): " + str(min_buy) + "; 利润率: " + entry_money_rate_str
        print content
        send_mail(content)
    #print '%.2f%%' % (entry_money_rate * 100)
    #entry_money_rate = (Decimal(min_sell) - (min_sell+min_buy) * 0.005) / min_buy 
    #print entry_money_rate
    #(售价-(售价＋成本) * 0.5%)/成本 > 4

    #"卖出价格(出售): " + + "成本价格(收购): " + + 


# 卖出价格(出售)
def find_min_sell(date):
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
        sql = "SELECT min(price) as min_price FROM `t_btc_sell`  WHERE  date = '%s' " % (date)
        print sql
        #sql = "INSERT INTO `ecs_t_marathon` (`name`, `start_run_time`) VALUES ('%s', '%s')" % (name, start_run_time)
        cur.execute(sql)
        conn.commit()
        result = cur.fetchone()
        return result[0]
        
        cur.close()
        conn.close()
    except Exception, e:
        print e.message
    return False

# 成本价格(收购)
def find_min_buy(date):
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
        sql = "SELECT min(price) as min_price FROM `t_btc_buy`  WHERE  date = '%s' " % (date)
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



def crawl_start():
    start_monitor()


def main():
    crawl_start();

if __name__ == '__main__':
    main()