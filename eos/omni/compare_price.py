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
from decimal import *

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


mailto_list = ['changaiqing@vip.163.com','249400834@qq.com']
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

def crawl_enter_sell():
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
            return price_sell
            break


    except Exception, e:
        print e.message

    return 0

def crawl_enter_buy():
    result={}
    header = {
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36',
        'Host': 'otcbtc.com',
    }
    response = requests.get('https://otcbtc.com/buy_offers?currency=eos&fiat_currency=cny&payment_type=all', headers=header, verify=False)
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
            price_buy = price.get_text().strip().replace(',','')

            minimum_amount = item.find('li',class_="minimum-amount")
            minimum_amount.span.extract()
            minimum_amount.span.extract()
            min_single =  minimum_amount.get_text().strip().split('-')[0].strip().replace(',','')
            max_single =  minimum_amount.get_text().strip().split('-')[1].strip().replace(',','')

            buy_link = item.find('li',class_="buy-button")
            sell_id = buy_link.a['href'].split('?')[0].split('/')[2]

            return price_buy
            break


    except Exception, e:
        print e.message

    return 0

def insert_rate(buy_min_price, sell_max_price, rate, date, date_hour, crawl_date ):
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
        sql = "INSERT INTO `omni_btc_compare_price` (`buy_min_price`, `sell_max_price`, `rate`, `date`, `date_hour`, `crawl_date`) VALUES ('%s', '%s', '%s', '%s', '%s', '%s')" % (buy_min_price, sell_max_price, rate, date, date_hour, crawl_date )
        #print sql
        #sql = "INSERT INTO `ecs_t_marathon` (`name`, `start_run_time`) VALUES ('%s', '%s')" % (name, start_run_time)
        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
    except Exception, e:
        print e.message


# 获取3天最低价的平均价格
def get_avg_min_price(date, limit = 3):
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
        sql = "SELECT * FROM `omni_btc_compare_price`  WHERE date = '%s' order by buy_min_price limit %s " % (date, limit)
        #sql = "INSERT INTO `ecs_t_marathon` (`name`, `start_run_time`) VALUES ('%s', '%s')" % (name, start_run_time)
        cur.execute(sql)
        conn.commit()
        result = cur.fetchall()

        avg_price = 0
        for item in result:
            avg_price += Decimal(item[2])

        return round(avg_price/limit,2)
        if result:
            return False
        else:
            return True
        
        cur.close()
        conn.close()
    except Exception, e:
        print e.message
    return True


def start_monitor():
    date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    crawl_date = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    crawl_date_hour = time.strftime('%Y-%m-%d %H:00:00',time.localtime(time.time()))
    
    
    #卖出价格(出售)
    max_sell =  crawl_enter_sell()

    # 成本价格(收购)
    min_buy =  crawl_enter_buy()
    
    max_sell = float(max_sell)
    min_buy = float(min_buy)
    entry_money_rate = (max_sell - (max_sell + min_buy) * (0.005)) / min_buy
    entry_money_rate_str = '%.2f%%' % (entry_money_rate * 100)

    entry_money_rate_spec =  min_buy / max_sell

    #content = "卖出价格(出售): " + str(max_sell) + "; 成本价格(收购): " + str(min_buy) + "; 利润率: " + entry_money_rate_str
    #print content
    
    insert_rate(min_buy, max_sell, round(entry_money_rate * 100,2), date, crawl_date_hour, crawl_date)

    # 售卖价格大于收购价格 1.2元 发送通知消息
    if ((max_sell - min_buy) > 1.2):
        key_flag = str(max_sell) + str(min_buy) + str(entry_money_rate_str) + str(crawl_date_hour)
        is_send = find_send_refer(key_flag)
        if(is_send and check_send_range()):
            content = "\n卖出价格(出售): " + str(max_sell) + ";\n成本价格(收购): " + str(min_buy) + ";\n 利润率: " + entry_money_rate_str
            print content
            send_mail(content)
            insert_send_refer(key_flag, date, crawl_date)
            send_wechat(content);
    


    # 收购价格低于前三天的平均最低价格,发送通知消息
    avg_min_pricd = get_avg_min_price(date)
    if(min_buy <= avg_min_pricd):
        key_flag = str(min_buy) + str(avg_min_pricd) + str(crawl_date_hour)
        print key_flag
        is_send = find_send_refer(key_flag)
        if(is_send and check_send_range()):
            content = "\n成本价格(收购): " + str(min_buy) + ";\n前三天的平均最低价格: " + str(avg_min_pricd)
            print content
            send_mail(content)
            insert_send_refer(key_flag, date, crawl_date)
            send_wechat(content);


    # 
    # if(entry_money_rate * 100 >= 104 or entry_money_rate_spec * 100 <= 97):
    #     content = "卖出价格(出售): " + str(max_sell) + "; 成本价格(收购): " + str(min_buy) + "; 利润率: " + entry_money_rate_str
    #     print content
        
    #     

  
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


def check_send_range():
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
    print resp


def crawl_start():
    print "start : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    start_monitor()

def main():
    crawl_start();

if __name__ == '__main__':
    main()