#!/usr/bin/python
#coding:utf-8
# OTCBTC 
# 市场价格、最近成交价格、 当前卖出价格、当前买入价格

import sys,os
# sys.path.append("../../platform/")
sys.path.append("../../common/otcbtc")
sys.path.append("../../common")
reload(sys)
sys.setdefaultencoding('utf-8')

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

import random

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)



from global_setting import *
from util import *


user_agent_list = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)",
    "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11"
]

# 卖出价格 对庄家来说(发布广告者)
def get_trade_sell_price(symbol):
    result={}
    header = {
        'Accept-Language': 'zh-CN,zh;q=0.9',
        #'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36',
        'Host': 'otcbtc.com',
    }
    header['User-Agent'] = random.sample(user_agent_list, 1)
    url = 'https://otcbtc.com/sell_offers?currency=%s&fiat_currency=cny&payment_type=all' % (symbol) 
    response = requests.get(url, headers=header, verify=False)
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

# 买入价格 对庄家来说(发布广告者)
def get_trade_buy_price(symbol):
    result={}
    header = {
        'Accept-Language': 'zh-CN,zh;q=0.9',
        #'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36',
        'Host': 'otcbtc.com',
    }
    header['User-Agent'] = random.sample(user_agent_list, 1)
    url = 'https://otcbtc.com/buy_offers?currency=%s&fiat_currency=cny&payment_type=all' % (symbol) 
    response = requests.get(url, headers=header, verify=False)
    if response.status_code != 200:
        return result

    try:
        soup = BeautifulSoup(response.text, "html.parser")
        info_list = soup.find_all('ul',class_="list-content")
        date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
        crawl_date = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        for key,item in enumerate(info_list):
            price = item.find('li',class_="price")
            price.span.extract()
            price.span.extract()
            price_sell = price.get_text().strip().replace(',','')


            minimum_amount = item.find('li',class_="minimum-amount")
            minimum_amount.span.extract()
            minimum_amount.span.extract()
            min_amount =  minimum_amount.get_text().strip().split('-')[0].strip().replace(',','')
            max_amount =  minimum_amount.get_text().strip().split('-')[1].strip().replace(',','')
            
            buy_link = item.find('li',class_="buy-button")
            buy_id = buy_link.a['href'].split('?')[0].split('/')[2]
            return price_sell
            break


    except Exception, e:
        print e.message

    return 0


def format_price(price_info):
    price = 0
    if(price_info.find('.') > 0):
        price = price_info.replace(',','')
    else:   
        price = 0
    
    return price

# 市场价格
def get_market_price():

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
        market_info = []
        for key,item in enumerate(info_list):
            for key_c, content in enumerate(item.find_all('tr')):
                if(key_c > 0):

                    item_0 = {}
                    currency = content.find_all('td')[0].text.strip()
                    item_0['currency'] = currency
                    item_0['bourse'] = "CoinMarketcap"
                    item_0['price'] = format_price(content.find_all('td')[1].text.strip().split(" ")[0]) 
                    market_info.append(item_0)

                    item_1 = {}
                    item_1['currency'] = currency
                    item_1['bourse'] = "Bitfinex"
                    item_1['price'] = format_price(content.find_all('td')[2].text.strip().split(" ")[0])
                    market_info.append(item_1)

                    item_2 = {}
                    item_2['currency'] = currency
                    item_2['bourse'] = "Bitstamp"
                    item_2['price'] = format_price(content.find_all('td')[3].text.strip().split(" ")[0]) 

                    market_info.append(item_2)
       
        return market_info
    except Exception as e:
        print e
    return False


def split_market_price(market_price_info, symbol):
    item_conn = []
    for key,item in enumerate(market_price_info):
        if(symbol == item['currency']):
            item_conn.append(item)

    return item_conn


#入口
def start():
    print "start : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    market_price_info = get_market_price()
    symbols = get_symbols()
    all_price_info = []
    for key,item in enumerate(symbols):
        symbol = item['symbol']
        sell_price = get_trade_sell_price(symbol)
        buy_price = get_trade_buy_price(symbol)
        item = {}
        item['sell_price'] = sell_price 
        item['buy_price'] = buy_price
        item['symbol'] = symbol
        market_price_json = split_market_price(market_price_info, symbol)
        item['market_price'] = json.dumps(market_price_json)
        all_price_info.append(item)

    v_content = view_content(all_price_info)
    if (allow_send_time()):
        send_wechat(v_content)
    print "end : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

def view_content(all_price_info):
    content = "\nOTCBTC 平台"
    for key,item in enumerate(all_price_info):
        row =   "\n币种: " + str(item['symbol']) + "; " + "卖出价格: " + str(item['sell_price']) + "; " + "买入价格: " + str(item['buy_price'])

        # market_row = ";\n市场价格"
        # for key,item_m in enumerate(json.loads(item['market_price'])):
        #     m_row = ";\n  " + "交易所: " + str(item_m['bourse']) + "; " + "价格: " + str(item_m['price'])
        #     market_row += m_row
        # row += market_row
        content += row
    return content


def main():
    start();

if __name__ == '__main__':
    main()