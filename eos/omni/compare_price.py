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
        print sql
        #sql = "INSERT INTO `ecs_t_marathon` (`name`, `start_run_time`) VALUES ('%s', '%s')" % (name, start_run_time)
        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
    except Exception, e:
        print e.message


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

    content = "卖出价格(出售): " + str(max_sell) + "; 成本价格(收购): " + str(min_buy) + "; 利润率: " + entry_money_rate_str
    print content
    #key_flag = str(max_sell) + str(min_buy) + entry_money_rate_str

    insert_rate(min_buy, max_sell, round(entry_money_rate * 100,2), date, crawl_date_hour, crawl_date)


    # if(entry_money_rate * 100 >= 104 or entry_money_rate_spec * 100 <= 97):
    #     content = "卖出价格(出售): " + str(max_sell) + "; 成本价格(收购): " + str(min_buy) + "; 利润率: " + entry_money_rate_str
    #     print content
        
    #     is_send = find_send_refer(key_flag)
    #     if(is_send):
    #         send_mail(content)
    #         insert_send_refer(key_flag, date, crawl_date)
    #         send_wechat(max_sell, min_buy, entry_money_rate_str);

            
# def send_wechat(max_sell, min_buy, entry_money_rate_str):
#     post_url = 'https://www.datasource.top/api/portal/btc/send'
    
#     headers = {
#         'content-type': 'application/x-www-form-urlencoded',
#     }

#     p_data = {
#         'max_sell':max_sell,
#         'min_buy':min_buy,
#         'entry_money_rate_str':entry_money_rate_str
#     }
#     data_u = urllib.urlencode(p_data)
#     resp = requests.post(post_url, data=data_u, headers=headers)
#     print resp.content
#     return resp.content

def crawl_start():
    print "start : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    start_monitor()

def main():
    crawl_start();

if __name__ == '__main__':
    main()