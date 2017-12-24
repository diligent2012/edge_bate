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
import random

import smtplib
from email.mime.text import MIMEText
from email.header import Header
from decimal import *

import urllib
import urllib2
import json
import requests


##################以下为现在的逻辑

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


user_agent_list = ["Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
                      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
                      "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
                      "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)",
                      "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
                      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11"
                      ]

def crawl_enter_sell():
    result={}
    header = {
        'Accept-Language': 'zh-CN,zh;q=0.9',
        #'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36',
        'Host': 'otcbtc.com',
    }
    header['User-Agent'] = random.sample(user_agent_list, 1)

    response = requests.get('https://otcbtc.com/sell_offers?currency=eos&fiat_currency=cny&payment_type=all', headers=header, verify=False)
    if response.status_code != 200:
        return result

    try:
        soup = BeautifulSoup(response.text, "html.parser")
        info_list = soup.find_all('ul',class_="list-content")
        date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
        crawl_date = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        for key,item in enumerate(info_list):
            #print item
            price = item.find('li',class_="price")
            price.span.extract()
            price.span.extract()
            price_sell = price.get_text().strip().replace(',','')


            minimum_amount = item.find('li',class_="minimum-amount")
            minimum_amount.span.extract()
            minimum_amount.span.extract()
            min_amount =  minimum_amount.get_text().strip().split('-')[0].strip().replace(',','')
            max_amount =  minimum_amount.get_text().strip().split('-')[1].strip().replace(',','')
            #print min_amount, max_amount
            
            buy_link = item.find('li',class_="buy-button")
            buy_id = buy_link.a['href'].split('?')[0].split('/')[2]
            print price_sell
            return price_sell
            break


    except Exception, e:
        print e.message

    return 0


def insert_send_refer(flag, date, crawl_date):
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
            user='omni_manage_pro',
            passwd='!omni123456manageMysql.pro',
            db ='z_omni_manage_pro',
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


def find_order_buy():
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
        sql = "SELECT * FROM `omni_btc_buy`  WHERE is_sell = 9 and is_out = 1"
        print sql
        cur.execute(sql)
        conn.commit()
        result = cur.fetchall()
        return result
        
        cur.close()
        conn.close()
    except Exception, e:
        print e.message
    return False


def insert_buy_rate(buy_id, min_sell_price, rate, rate_price, rate_total_price, cal_date):
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
        sql = "INSERT INTO `omni_btc_buy_rate` (`buy_id`, `min_sell_price`, `rate`, `rate_price`, `rate_total_price`, `cal_date`) VALUES ('%s', '%s', '%s', '%s', '%s')" % (buy_id, min_sell_price, rate, rate_price, rate_total_price, cal_date)
        print sql
        #sql = "INSERT INTO `ecs_t_marathon` (`name`, `start_run_time`) VALUES ('%s', '%s')" % (name, start_run_time)
        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
    except Exception, e:
        print e.message


def find_rate_is_cal(buy_id, rate):
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
        sql = "SELECT * FROM `omni_btc_buy_rate`  WHERE buy_id = '%s' and rate = %s" % (buy_id, rate)
        print sql
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


# 开始监控
def start_monitor():

    # 开始监控 
    # 出售 逻辑
    # 获取待出售的订单
    # 获取当前sell、buy的最低价格
    # 获取当前的价格、按照公式推出当前最低的售卖价格
    # 售卖价格和当前的sell价格对比。
    # 售卖价格和当前的buy价格对比。
    # 发送邮件和微信提醒

    order_buy = find_order_buy()
    
    #print order_buy
    date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    crawl_date = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    #rate_list = [1.03,1.05,1.10,1.15,1.20]
    rate_list = [1.03,1.02,1.01]
    for item_buy in order_buy:
        price = item_buy[3] # 购买价格
        buy_quantity = item_buy[2] # 购买数量
        buy_id = item_buy[0]# 购买表主键

        curr_min_sell_price =  crawl_enter_sell() # 当前售卖最低价格
        curr_min_sell_price = float(curr_min_sell_price);

        for rate in rate_list:
            sell_price = round(float(rate) * float(price) * 0.995,2)
            rate_price = sell_price - price
            rate_total_price = rate_price * float(buy_quantity)
            is_cal = find_rate_is_cal(buy_id, rate)
            if(is_cal):
                insert_buy_rate(buy_id, sell_price, rate, rate_price, rate_total_price, crawl_date)

            if (curr_min_sell_price >= sell_price):
                key_flag = str(curr_min_sell_price) + str(price) + str(rate_price)
                is_send = find_send_refer(key_flag)
                if(is_send):
                    content = "\n当前售卖价格: " + str(curr_min_sell_price) + ";\n"+"当初购买价格: " + str(price) + ";\n"+" 利润: " + str(rate_price) + ";\n"+" 对应产品ID为: " + str(buy_id)
                    print content
                    send_mail(content)
                    insert_send_refer(key_flag, date, crawl_date)
                    send_wechat(content);

            
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



def crawl_start():
    print "start : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    start_monitor()

def main():
    crawl_start();

if __name__ == '__main__':
    main()