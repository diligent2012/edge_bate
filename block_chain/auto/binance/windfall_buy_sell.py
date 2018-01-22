#!/usr/bin/python
#coding:utf-8
# 币安平台自动交易
# 通过K线同时买入和卖出

# 循环不同的账户
# # 循环不同的币种
# # # 获取前三天的平均最高价格、最低价格
# # #
# # # 买入1单 价格最低 设置委托价格
# # # 卖出1单 价格最高 设置委托价格
# 当天,这两单如果完成,则ok;
# 如果没有完成,取消订单,重新发出
# 如果 只完成一个买入或者只完成一个卖出。则全部取消。重新发出

# select min(data_price),max(data_price), (max(data_price) - min(data_price))/min(data_price)  from omni_btc_binance_recent_trades_data where data_time >= 1516032000000 and data_time <= 1516118399000


import sys,os
sys.path.append(os.path.abspath("../../lib"))
sys.path.append(os.path.abspath("../../common"))
reload(sys)
sys.setdefaultencoding('utf-8')
from binance_lib.client import Client
from binance_lib.exceptions import BinanceAPIException, BinanceRequestException, BinanceWithdrawException
import time
from binance_lib.enums import *
from decimal import *
import traceback

from datetime import datetime
from datetime import timedelta

from setting import *
from db import *
from util import *
from helper import *

# 开始买入卖出
def start_windfall():
    
    try:
        account_list = get_windfall_account_list()
        # 循环不同的账户
        for key,a_item in enumerate(account_list):

            client = Client(a_item['api_key'], a_item['api_secret'])
            account = a_item['account']
            qty = a_item['qty']
            binance_symbols = a_item['allow_symbol']
            # 循环不同的币种
            for key,s_item in enumerate(binance_symbols): 

                symbol = s_item['symbol']
                all_max_min_price = get_day_interval_all_klines(client, s_item['symbol'])
                sug_max_price, sug_min_price, rate = oper_max_min_price(all_max_min_price)

                if (rate > 0.1):
                    print sug_max_price, sug_min_price, rate

                    min_price_rate = round( Decimal(1.0) + Decimal(rate / 2) * Decimal(0.2), 4)
                    max_price_rate = round( Decimal(1.0) - Decimal(rate / 2) * Decimal(0.2), 4)
                    print min_price_rate, max_price_rate

                    last_max_price = round(Decimal(sug_max_price) * Decimal(max_price_rate), 6)
                    last_min_price = round(Decimal(sug_min_price) * Decimal(min_price_rate), 6)
                    print "最低价格: %s" % last_min_price
                    print "最高价格: %s" % last_max_price
                    print "涨幅: %s" % round( (last_max_price - last_min_price)/last_min_price , 4)

                    

                else:
                    print "低于0.1"

    except Exception as e:  
        send_exception(traceback.format_exc())


def buy_order(client, symbol, buy_price, qty):
    try:
        order_symbol = symbol
        order_side = SIDE_BUY
        order_type = ORDER_TYPE_STOP_LOSS_LIMIT
        order_timeInForce = TIME_IN_FORCE_GTC
        order_price = buy_price  # 止盈价格
        order_stopPrice = buy_price  # 触发价格
        order_quantity = qty

        create_stop_buy_order(client, symbol, order_side, order_type, order_timeInForce, order_quantity, order_price, order_stopPrice)
    except Exception as e:  
        send_exception(traceback.format_exc())

def oper_max_min_price(all_max_min_price):

    sug_max_price = 0.0
    sug_min_price = 0.0
    try:
        for key,p_item in enumerate(all_max_min_price): 

            min_price = p_item['min_price']
            max_price = p_item['max_price']

            if (key == 0 ):
                sug_max_price = max_price
                sug_min_price = min_price

            if(sug_max_price < max_price):
                sug_max_price = max_price

            if(sug_min_price > min_price):
                sug_min_price = min_price

        rate =  round( (Decimal(sug_max_price) - Decimal(sug_min_price)) / Decimal(sug_min_price), 4)
    except Exception as e:
        send_exception(traceback.format_exc())
    return sug_max_price, sug_min_price, rate



def get_day_interval_all_klines(client, symbol):
    all_max_min_price = []
    try:
        multi_datetimes = get_multi_datetime(2,True)
        
        for key,m_item in enumerate(multi_datetimes):

            day_hour_intervals =  get_day_hour_interval(m_item['start_date'], m_item['start_time'], m_item['end_date'], m_item['end_time'])

            day_max_price = 0.0
            day_min_price = 0.0

            for key,i_item in enumerate(day_hour_intervals):

                min_price, max_price = get_all_klines(client, symbol, i_item['start_time'], i_item['end_time'])
                if (min_price != 0 and max_price != 0):
                    if (key == 0 ):
                        day_max_price = max_price
                        day_min_price = min_price

                    if(day_max_price < max_price):
                        day_max_price = max_price

                    if(day_min_price > min_price):
                        day_min_price = min_price

            item = {}
            item["max_price"] = day_max_price
            item["min_price"] = day_min_price
            item["date"] = m_item['start_date']
            item["rate"] = round( (day_max_price - day_min_price) / day_min_price, 4)
            all_max_min_price.append(item)
    except Exception as e:
        send_exception(traceback.format_exc())
    return all_max_min_price


# 获取k线数据
def get_all_klines(client, symbol, start_time, end_time):

    max_price = 0.0
    min_price = 0.0
    close_max_price = 0.0 
    close_min_price = 0.0
    try:
        klines = client.get_klines(symbol = symbol, interval = KLINE_INTERVAL_1MINUTE, startTime = start_time, endTime = end_time)

        for key,item in enumerate(klines):
            open_time_ori = item[0]
            open_time = format_time(int(open_time_ori))
            
            open_price = item[1]
            high_price = item[2]
            low_price = item[3]
            close_price = item[4]

            close_time_ori = item[6]
            close_time = format_time(int(close_time_ori))

            # if(0 == key):
            #     print open_time
            # if(len(klines) - 1 == key):
            #     print open_time

            if(0 == key):
                max_price = Decimal(high_price)
                min_price = Decimal(low_price)

                close_max_price = Decimal(close_price)
                close_min_price= Decimal(close_price)

            if (start_time < open_time_ori and open_time_ori < end_time):

                if(max_price < Decimal(high_price)):
                    max_price = Decimal(high_price)
                if(min_price > Decimal(low_price)):
                    min_price = Decimal(low_price)

                if(close_max_price < Decimal(close_price)):
                    close_max_price = Decimal(close_price)
                if(close_min_price > Decimal(close_price)):
                    close_min_price = Decimal(close_price)
    
    except Exception as e:
        send_exception(traceback.format_exc())

    return min_price, max_price

# 获取每小时间隔 根据每天开始日期和结束日期
def get_day_hour_interval(start_date, start_time, end_date, end_time):
    all_day_hour = []
    try:
        start_date = datetime.strptime(start_date,'%Y-%m-%d %H:%M:%S')
        end_date = datetime.strptime(end_date,'%Y-%m-%d %H:%M:%S')  

        start_date_flag = start_date
        start_time_flag = start_time

        end_date_flag = end_date
        end_time_flag = end_time

        for i in range(23):
            interval = (i + 1)
            interval_hour = start_date + timedelta(hours = interval)
            interval_hour_time = int(time.mktime(time.strptime(interval_hour.strftime('%Y-%m-%d %H:%M:%S'), "%Y-%m-%d %H:%M:%S"))) * 1000

            if (interval_hour_time < end_time):
                item = {}
                item["start_date"] = start_date_flag
                item["start_time"] = start_time_flag
                item["end_date"] = interval_hour
                item["end_time"] = interval_hour_time
                all_day_hour.append(item)

                start_date_flag = interval_hour
                start_time_flag = interval_hour_time

        item_e = {}
        item_e["start_date"] = start_date_flag
        item_e["start_time"] = start_time_flag
        item_e["end_date"] = end_date_flag
        item_e["end_time"] = end_time_flag
        all_day_hour.append(item_e)
    except Exception as e:
        send_exception(traceback.format_exc())

    return all_day_hour

# 获取以日期为单位 当天
def get_curr_today_datetime():
    try:
        today = datetime.now()

        start_today = today.strftime('%Y-%m-%d 00:00:00')
        start_today_time = int(time.mktime(time.strptime(start_today, "%Y-%m-%d %H:%M:%S"))) * 1000

        end_today = today + timedelta(hours = 1)
        end_today = end_today.strftime('%Y-%m-%d %H:00:00')
        end_today_time = int(time.mktime(time.strptime(end_today, "%Y-%m-%d %H:%M:%S"))) * 1000

        today_item = {}
        today_item["start_time"] = start_today_time
        today_item["end_time"] = end_today_time
        today_item["start_date"] = start_today
        today_item["end_date"] = end_today
        today_item["key"] = 0

        return today_item
    except Exception as e:
        send_exception(traceback.format_exc())
    return False

# 获取以日期为单位 前几天
def get_multi_datetime(num, is_today = False):
    multi_datetime = []
    try:
        today = datetime.now()

        if (is_today):
            curr_today_datetime = get_curr_today_datetime()
            if (curr_today_datetime):
                multi_datetime.append(curr_today_datetime)

        if (num != 0):
            for i in range(num):
                yesterday = today - timedelta(days = (i + 1)) 
                start_yesterday = yesterday.strftime('%Y-%m-%d 00:00:00')
                end_yesterday =  yesterday.strftime('%Y-%m-%d 23:59:59') 
                start_yesterday_time = int(time.mktime(time.strptime(start_yesterday, "%Y-%m-%d %H:%M:%S"))) * 1000
                end_yesterday_time =  int(time.mktime(time.strptime(end_yesterday, "%Y-%m-%d %H:%M:%S"))) * 1000

                yesterday_item = {}
                yesterday_item["start_time"] = start_yesterday_time
                yesterday_item["end_time"] = end_yesterday_time
                yesterday_item["start_date"] = start_yesterday
                yesterday_item["end_date"] = end_yesterday
                yesterday_item["key"] = i + 1
                multi_datetime.append(yesterday_item)
    except Exception as e:
        send_exception(traceback.format_exc())
    return multi_datetime


# 入口方法
def main():
    print "start : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    start_windfall()
    print "end : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

if __name__ == '__main__':
    main() 
