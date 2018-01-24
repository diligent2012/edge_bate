#!/usr/bin/python
#coding:utf-8
import sys  
sys.path.append("..")
reload(sys)
sys.setdefaultencoding('utf-8')
import sqlite3
import requests
import json
from bs4 import BeautifulSoup
import re
import MySQLdb
import time
import random
from datetime import datetime
from datetime import timedelta
import traceback

from util import *

# 插入 github eos code 变动记录
def insert_btc_eos_github_code(watch, star, fork, commits, branches, releases, contributors, date):
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
        sql = "INSERT INTO `omni_btc_eos_github_code` (`watch`, `star`, `fork`, `commits`, `branches`, `releases`, `contributors`, `date`) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (watch, star, fork, commits, branches, releases, contributors, date)
        cur.execute(sql)
        conn.commit()
        result = cur.fetchall()
        if result:
            return True
        cur.close()
        conn.close()
    except Exception as e:
        send_exception(traceback.format_exc())
    return False

# 查询 上一次 代码变更数据
def find_btc_eos_github_code_prev_one():
    try:
        conn= MySQLdb.connect(
            host='127.0.0.1',
            port = 3306,
            user='omni_manage_pro',
            passwd='!omni123456manageMysql.pro',
            db ='z_omni_manage_pro',
        )
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('set names utf8') #charset set code. it is not nessary now
        sql = "SELECT * FROM `omni_btc_eos_github_code`  order by date desc " 
        #print sql
        cur.execute(sql)
        conn.commit()
        result = cur.fetchone()
        return result
        cur.close()
        conn.close()
    except Exception as e:
        send_exception(traceback.format_exc())
    return False

# 插入 github eos code 变动记录
def insert_btc_eos_github_code_tag(tag, date):
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
        sql = "INSERT INTO `omni_btc_eos_github_code_tag` (`tag`, `date`) VALUES ('%s', '%s')" % (tag, date)
        cur.execute(sql)
        conn.commit()
        result = cur.fetchall()
        if result:
            return True
        cur.close()
        conn.close()
    except Exception as e:
        send_exception(traceback.format_exc())
    return False

# 查询 
def find_btc_eos_github_code_tag(tag):
    try:
        conn= MySQLdb.connect(
            host='127.0.0.1',
            port = 3306,
            user='omni_manage_pro',
            passwd='!omni123456manageMysql.pro',
            db ='z_omni_manage_pro',
        )
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('set names utf8') #charset set code. it is not nessary now
        sql = "SELECT * FROM `omni_btc_eos_github_code_tag` WHERE tag = '%s' order by date desc " % (tag)
        #print sql
        cur.execute(sql)
        conn.commit()
        result = cur.fetchone()
        if result:
            return True
        cur.close()
        conn.close()
    except Exception as e:
        send_exception(traceback.format_exc())
    return False

def insert_otcbtc_trade_record_refer(flag, date):
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
        sql = "INSERT INTO `omni_btc_otcbtc_trade_record_refer` (`flag`, `date`) VALUES ('%s', '%s')" % (flag, date)
        #print sql
        #sql = "INSERT INTO `ecs_t_marathon` (`name`, `start_run_time`) VALUES ('%s', '%s')" % (name, start_run_time)
        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        send_exception(traceback.format_exc())

def find_otcbtc_trade_record_refer(flag, crawl_date_refer):
    try:
        conn= MySQLdb.connect(
            host='127.0.0.1',
            port = 3306,
            user='omni_manage_pro',
            passwd='!omni123456manageMysql.pro',
            db ='z_omni_manage_pro',
        )
        cur = conn.cursor(MySQLdb.cursors.DictCursor)

        cur.execute('set names utf8') #charset set code. it is not nessary now
        sql = "SELECT * FROM `omni_btc_otcbtc_trade_record_refer`  WHERE flag = '%s' and date >= '%s' " % (flag, crawl_date_refer)
        cur.execute(sql)
        conn.commit()
        result = cur.fetchall()
        if result:
            return False
        else:
            return True
        
        cur.close()
        conn.close()
    except Exception as e:
        send_exception(traceback.format_exc())
    return True

def insert_otcbtc_trade_record(quantity, currency, duration, date, crawl_date, date_hour):
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
        sql = "INSERT INTO `omni_btc_otcbtc_trade_record` (`quantity`, `currency`, `duration`, `date`, `crawl_date`, `date_hour`) VALUES ('%s', '%s', '%s', '%s', '%s', '%s')" % (quantity, currency, duration, date, crawl_date, date_hour)
        #print sql
        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        send_exception(traceback.format_exc())

# 查询是否有正在买的订单
def find_btc_binance_order_buying(account, symbol):
    try:
        conn= MySQLdb.connect(
            host='127.0.0.1',
            port = 3306,
            user='omni_manage_pro',
            passwd='!omni123456manageMysql.pro',
            db ='z_omni_manage_pro',
        )
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('set names utf8') #charset set code. it is not nessary now
        sql = "SELECT * FROM `omni_btc_binance_order`  WHERE side = 'BUY'  and status = 'NEW'  and account = '%s' and symbol = '%s' order by time desc " % (account, symbol)
        #print sql
        cur.execute(sql)
        conn.commit()
        result = cur.fetchall()
        if result:
            return result
        cur.close()
        conn.close()
    except Exception as e:
        send_exception(traceback.format_exc())
    return False

# 查询是否有正在卖的订单
def find_btc_binance_order_selling(account, symbol):
    try:
        conn= MySQLdb.connect(
            host='127.0.0.1',
            port = 3306,
            user='omni_manage_pro',
            passwd='!omni123456manageMysql.pro',
            db ='z_omni_manage_pro',
        )
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('set names utf8') #charset set code. it is not nessary now
        sql = "SELECT * FROM `omni_btc_binance_order`  WHERE side = 'SELL'  and status = 'NEW'  and account = '%s' and symbol = '%s' order by time desc " % (account, symbol)
        #sql = "SELECT * FROM `omni_btc_binance_order`  WHERE side = 'SELL' order by time desc " 
        #print sql
        cur.execute(sql)
        conn.commit()
        result = cur.fetchall()
        if result:
            return result
        cur.close()
        conn.close()
    except Exception as e:
        send_exception(traceback.format_exc())
    return False

# 获取最近一次卖出的交易数据
def find_btc_binance_order_sell_newest_one(account, symbol):
    try:
        conn= MySQLdb.connect(
            host='127.0.0.1',
            port = 3306,
            user='omni_manage_pro',
            passwd='!omni123456manageMysql.pro',
            db ='z_omni_manage_pro',
        )
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('set names utf8') #charset set code. it is not nessary now
        sql = "SELECT * FROM `omni_btc_binance_order`  WHERE side = 'SELL'  and status = 'FILLED' and account = '%s' and symbol = '%s' order by time desc " % (account, symbol)
        #print sql
        cur.execute(sql)
        conn.commit()
        result = cur.fetchone()
        return result
        cur.close()
        conn.close()
    except Exception as e:
        send_exception(traceback.format_exc())
    return False

# 查询买入时, 止盈设置纪录
def find_btc_binance_order_stop_buy_record_newest_one(account, symbol):
    try:
        conn= MySQLdb.connect(
            host='127.0.0.1',
            port = 3306,
            user='omni_manage_pro',
            passwd='!omni123456manageMysql.pro',
            db ='z_omni_manage_pro',
        )
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('set names utf8') #charset set code. it is not nessary now
        #sql = "SELECT * FROM `omni_btc_binance_order_stop_record`  WHERE price = '%s' and stopPrice = '%s' and origQty = '%s' and clientOrderId = '%s' " % (sell_price, stop_sell_price, buy_qty, newClientOrderId)
        sql = "SELECT * FROM `omni_btc_binance_order_stop_buy_record` WHERE account = '%s' and symbol = '%s' order by transactTime desc " % (account, symbol)
        #print sql
        cur.execute(sql)
        conn.commit()
        result = cur.fetchone()
        return result
        cur.close()
        conn.close()
    except Exception as e:
        send_exception(traceback.format_exc())
    return False

# 插入 买入时, 止盈设置纪录
def insert_btc_binance_order_stop_buy_record(data, account):
    try:
        
        orderId = data['orderId']
        clientOrderId = data['clientOrderId']

        origQty = data['origQty']
        symbol = data['symbol']

        side = data['side']
        timeInForce = data['timeInForce']

        status = data['status']
        stopPrice = data['stopPrice']

        transactTime = data['transactTime']
        o_type = data['type']

        price = data['price']
        executedQty = data['executedQty']

        conn= MySQLdb.connect(
            host='127.0.0.1',
            port = 3306,
            user='omni_manage_pro',
            passwd='!omni123456manageMysql.pro',
            db ='z_omni_manage_pro',
        )
        cur = conn.cursor()
        cur.execute('set names utf8') #charset set code. it is not nessary now
        sql = "INSERT INTO `omni_btc_binance_order_stop_buy_record` (`orderId`,`clientOrderId`,`origQty`,`executedQty`,`symbol`,`side`,`timeInForce`,`status`,`stopPrice`,`transactTime`,`o_type`,`price`,`account`) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (orderId,clientOrderId,origQty,executedQty,symbol,side,timeInForce,status,stopPrice,transactTime,o_type,price, account)
        cur.execute(sql)
        conn.commit()
        result = cur.fetchall()
        return result
        cur.close()
        conn.close()
    except Exception as e:
        send_exception(traceback.format_exc())
    return False

# 插入 订单 数据
def insert_btc_binance_order_stop_sell_record(data, parentClientOrderId):
    try:
        
        orderId = data['orderId']
        clientOrderId = data['clientOrderId']


        origQty = data['origQty']
        symbol = data['symbol']

        side = data['side']
        timeInForce = data['timeInForce']

        status = data['status']
        stopPrice = data['stopPrice']

        transactTime = data['transactTime']
        o_type = data['type']

        price = data['price']
        executedQty = data['executedQty']

        conn= MySQLdb.connect(
            host='127.0.0.1',
            port = 3306,
            user='omni_manage_pro',
            passwd='!omni123456manageMysql.pro',
            db ='z_omni_manage_pro',
        )
        cur = conn.cursor()
        cur.execute('set names utf8') #charset set code. it is not nessary now
        sql = "INSERT INTO `omni_btc_binance_order_stop_sell_record` (`orderId`,`clientOrderId`,`origQty`,`executedQty`,`symbol`,`side`,`timeInForce`,`status`,`stopPrice`,`transactTime`,`o_type`,`price`,`parentClientOrderId`) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (orderId,clientOrderId,origQty,executedQty,symbol,side,timeInForce,status,stopPrice,transactTime,o_type,price, parentClientOrderId)
        cur.execute(sql)
        conn.commit()
        result = cur.fetchall()
        return result
        cur.close()
        conn.close()
    except Exception as e:
        send_exception(traceback.format_exc())
    return False



# 插入 订单 数据
def insert_btc_binance_order_limit_buy_sell_record(data, parentClientOrderId, account):
    try:
        
        orderId = data['orderId']
        clientOrderId = data['clientOrderId']

        origQty = data['origQty']
        symbol = data['symbol']

        side = data['side']
        timeInForce = data['timeInForce']

        status = data['status']

        transactTime = data['transactTime']
        o_type = data['type']

        price = data['price']
        executedQty = data['executedQty']

        conn= MySQLdb.connect(
            host='127.0.0.1',
            port = 3306,
            user='omni_manage_pro',
            passwd='!omni123456manageMysql.pro',
            db ='z_omni_manage_pro',
        )
        cur = conn.cursor()
        cur.execute('set names utf8') #charset set code. it is not nessary now
        sql = "INSERT INTO `omni_btc_binance_order_limit_buy_sell_record` (`orderId`,`clientOrderId`,`origQty`,`executedQty`,`symbol`,`side`,`timeInForce`,`status`,`transactTime`,`o_type`,`price`,`parentClientOrderId`,`account`) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (orderId,clientOrderId,origQty,executedQty,symbol,side,timeInForce,status,transactTime,o_type,price, parentClientOrderId, account)
        cur.execute(sql)
        conn.commit()
        result = cur.fetchall()
        return result
        cur.close()
        conn.close()
    except Exception as e:
        send_exception(traceback.format_exc())
    return False


# 获取上一次没有全部卖出的订单
def find_btc_binance_order_buy_newest_one_not_all_sell(account, symbol):
    try:
        conn= MySQLdb.connect(
            host='127.0.0.1',
            port = 3306,
            user='omni_manage_pro',
            passwd='!omni123456manageMysql.pro',
            db ='z_omni_manage_pro',
        )
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('set names utf8') #charset set code. it is not nessary now
        sql = "SELECT * FROM `omni_btc_binance_order`  WHERE is_up = 1 and executedQty !=  0.00000000 and side = 'SELL'  and status = 'CANCELED'  and account = '%s' and symbol = '%s' order by time desc " % (account, symbol)
        #print sql
        cur.execute(sql)
        conn.commit()
        result = cur.fetchone()
        return result
        cur.close()
        conn.close()
    except Exception as e:
        send_exception(traceback.format_exc())
    return False

# 获取上一次买入的订单
def find_btc_binance_order_buy_newest_one(account, symbol):
    try:
        conn= MySQLdb.connect(
            host='127.0.0.1',
            port = 3306,
            user='omni_manage_pro',
            passwd='!omni123456manageMysql.pro',
            db ='z_omni_manage_pro',
        )
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('set names utf8') #charset set code. it is not nessary now
        sql = "SELECT * FROM `omni_btc_binance_order`  WHERE is_up = 1 and side = 'BUY'  and status = 'FILLED'  and account = '%s' and symbol = '%s' order by time desc  " % (account, symbol)
        #print sql
        cur.execute(sql)
        conn.commit()
        result = cur.fetchone()
        return result
        cur.close()
        conn.close()
    except Exception as e:
        send_exception(traceback.format_exc())
    return False

# 获取上一次 卖出 止损 设置的信息
def find_btc_binance_order_stop_sell_record_newest_one(newClientOrderId):
    try:
        conn= MySQLdb.connect(
            host='127.0.0.1',
            port = 3306,
            user='omni_manage_pro',
            passwd='!omni123456manageMysql.pro',
            db ='z_omni_manage_pro',
        )
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('set names utf8') #charset set code. it is not nessary now
        #sql = "SELECT * FROM `omni_btc_binance_order_stop_record`  WHERE price = '%s' and stopPrice = '%s' and origQty = '%s' and clientOrderId = '%s' " % (sell_price, stop_sell_price, buy_qty, newClientOrderId)
        sql = "SELECT * FROM `omni_btc_binance_order_stop_sell_record`  WHERE parentClientOrderId = '%s' order by transactTime desc " % (newClientOrderId)
        #print sql
        cur.execute(sql)
        conn.commit()
        result = cur.fetchone()
        return result
        cur.close()
        conn.close()
    except Exception as e:
        send_exception(traceback.format_exc())
    return False

# 查询 最近交易 中最新的一条
def find_btc_binance_recent_trades_data_newest_one(symbol):
    try:
        conn= MySQLdb.connect(
            host='127.0.0.1',
            port = 3306,
            user='omni_manage_pro',
            passwd='!omni123456manageMysql.pro',
            db ='z_omni_manage_pro',
        )
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('set names utf8') #charset set code. it is not nessary now
        sql = "SELECT * FROM `omni_btc_binance_recent_trades_data` WHERE data_symbol = '%s' order by data_time desc" % (symbol)
        #print sql
        cur.execute(sql)
        conn.commit()
        result = cur.fetchone()
        return result
        cur.close()
        conn.close()
    except Exception as e:
        send_exception(traceback.format_exc())
    return False



# 查询 交易
def find_binance_recent_trades_data(data_id):
    try:
        conn= MySQLdb.connect(
            host='127.0.0.1',
            port = 3306,
            user='omni_manage_pro',
            passwd='!omni123456manageMysql.pro',
            db ='z_omni_manage_pro',
        )
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('set names utf8') #charset set code. it is not nessary now
        sql = "SELECT * FROM `omni_btc_binance_recent_trades_data` WHERE data_id = '%s' " % (data_id)
        #print sql
        cur.execute(sql)
        conn.commit()
        result = cur.fetchone()
        if result:
            return True
        cur.close()
        conn.close()
    except Exception as e:
        send_exception(traceback.format_exc())
    return False

# 记录 最近交易的数据
def insert_binance_recent_trades_data(data_isBuyerMaker, data_price, data_qty, data_time, data_id, data_isBestMatch, sync_time, change_rate, data_symbol):
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
        sql = "INSERT INTO `omni_btc_binance_recent_trades_data` (`data_isBuyerMaker`, `data_price`, `data_qty`, `data_time`, `data_id`, `data_isBestMatch`, `sync_time`, `change_rate`, `data_symbol`) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (data_isBuyerMaker, data_price, data_qty, data_time, data_id, data_isBestMatch, sync_time, change_rate, data_symbol)
        #print sql
        #sql = "INSERT INTO `ecs_t_marathon` (`name`, `start_run_time`) VALUES ('%s', '%s')" % (name, start_run_time)
        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        send_exception(traceback.format_exc())




# 查询 交易
def find_binance_recent_trades_data_rate(pk_id):
    try:
        conn= MySQLdb.connect(
            host='127.0.0.1',
            port = 3306,
            user='omni_manage_pro',
            passwd='!omni123456manageMysql.pro',
            db ='z_omni_manage_pro',
        )
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('set names utf8') #charset set code. it is not nessary now
        sql = "SELECT * FROM `omni_btc_binance_recent_trades_rate` WHERE pk_id = '%s' " % (pk_id)
        #print sql
        cur.execute(sql)
        conn.commit()
        result = cur.fetchone()
        if result:
            return True
        cur.close()
        conn.close()
    except Exception as e:
        send_exception(traceback.format_exc())
    return False


# 记录 最近交易的数据
def insert_binance_recent_trades_data_rate(max_price, min_price, max_trade_time, min_trade_time, rate, symbol, pk_id, sync_time):
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
        sql = "INSERT INTO `omni_btc_binance_recent_trades_rate` (`max_price`, `min_price`, `max_trade_time`, `min_trade_time`, `rate`, `symbol`, `pk_id`, `sync_time`) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (max_price, min_price, max_trade_time, min_trade_time, rate, symbol, pk_id, sync_time)
        #print sql
        #sql = "INSERT INTO `ecs_t_marathon` (`name`, `start_run_time`) VALUES ('%s', '%s')" % (name, start_run_time)
        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        send_exception(traceback.format_exc())


# 插入 资产 数据
def insert_btc_binance_asset(account, asset, free, locked, date):
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
        sql = "INSERT INTO `omni_btc_binance_asset` (`account`,`asset`,`free`,`locked`,`date`) VALUES ('%s', '%s', '%s', '%s', '%s')" % (account, asset, free, locked, date)
        cur.execute(sql)
        conn.commit()
        result = cur.fetchall()
        return result
        cur.close()
        conn.close()
    except Exception as e:
        send_exception(traceback.format_exc())
    return False

# 根据orderId查询交易订单
def find_btc_binance_order_record(orderId):
    try:

        conn= MySQLdb.connect(
            host='127.0.0.1',
            port = 3306,
            user='omni_manage_pro',
            passwd='!omni123456manageMysql.pro',
            db ='z_omni_manage_pro',
        )
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('set names utf8') #charset set code. it is not nessary now
        sql = "SELECT * FROM `omni_btc_binance_order`  WHERE orderId = '%s' " % (orderId)
        cur.execute(sql)
        conn.commit()
        result = cur.fetchone()
        return result
        cur.close()
        conn.close()
    except Exception as e:
        send_exception(traceback.format_exc())
    return False

# 插入 订单 数据
def insert_btc_binance_order(data):
    try:
        sellClientOrderId = data['sellClientOrderId']
        account = data['account']
        orderId = data['orderId']
        clientOrderId = data['clientOrderId']
        origQty = data['origQty']
        icebergQty = data['icebergQty']
        symbol = data['symbol']
        side = data['side']
        timeInForce = data['timeInForce']
        status = data['status']
        stopPrice = data['stopPrice']
        time = data['time']
        isWorking = data['isWorking']
        o_type = data['o_type']
        price = data['price']
        executedQty = data['executedQty']

        conn= MySQLdb.connect(
            host='127.0.0.1',
            port = 3306,
            user='omni_manage_pro',
            passwd='!omni123456manageMysql.pro',
            db ='z_omni_manage_pro',
        )
        cur = conn.cursor()
        cur.execute('set names utf8') #charset set code. it is not nessary now
        sql = "INSERT INTO `omni_btc_binance_order` (`account`,`sellClientOrderId`,`orderId`,`clientOrderId`,`origQty`,`icebergQty`,`executedQty`,`symbol`,`side`,`timeInForce`,`status`,`stopPrice`,`time`,`isWorking`,`o_type`,`price`) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (account,sellClientOrderId,orderId,clientOrderId,origQty,icebergQty,executedQty,symbol,side,timeInForce,status,stopPrice,time,isWorking,o_type,price)
        cur.execute(sql)
        conn.commit()
        result = cur.fetchall()
        return result
        cur.close()
        conn.close()
    except Exception as e:
        send_exception(traceback.format_exc())
    return False

# 更新 订单 所有信息
def update_btc_binance_order(data):
    try:

        orderId = data['orderId']
        status = data['status']
        time = data['time']
        isWorking = data['isWorking']

        origQty = data['origQty']
        icebergQty = data['icebergQty']
        executedQty = data['executedQty']

        conn= MySQLdb.connect(
            host='127.0.0.1',
            port = 3306,
            user='omni_manage_pro',
            passwd='!omni123456manageMysql.pro',
            db ='z_omni_manage_pro',
        )
        cur = conn.cursor()
        cur.execute('set names utf8') #charset set code. it is not nessary now
        sql = "UPDATE `omni_btc_binance_order` SET `status` = '%s',`time` = '%s', `isWorking` = '%s', `origQty` = '%s', `icebergQty` = '%s', `executedQty` = '%s'  WHERE orderId = '%s' " % (status, time, isWorking, origQty, icebergQty, executedQty, orderId)
        #print sql
        cur.execute(sql)
        conn.commit()
        result = cur.fetchall()
        return result
        cur.close()
        conn.close()
    except Exception as e:
        send_exception(traceback.format_exc())
    return False

# 查询是否有正在进行的订单
def find_btc_binance_order_is_up(account, start_auto_date):
    try:
        conn= MySQLdb.connect(
            host='127.0.0.1',
            port = 3306,
            user='omni_manage_pro',
            passwd='!omni123456manageMysql.pro',
            db ='z_omni_manage_pro',
        )

        cur = conn.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('set names utf8') #charset set code. it is not nessary now
        sql = "SELECT * FROM `omni_btc_binance_order`  WHERE is_up = 1 and stopPrice != 0.0 and account = '%s' and time > '%s' order by time desc" % (account, start_auto_date)
        #print sql
        cur.execute(sql)
        conn.commit()
        result = cur.fetchone()
        if result:
            return True
        cur.close()
        conn.close()
    except Exception as e:
        send_exception(traceback.format_exc())
    return False

# 查询买入订单 对应 的卖出订单
def find_btc_binance_order_sell_record(account, sellClientOrderId):
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
        sql = "SELECT * FROM `omni_btc_binance_order`  WHERE side = 'SELL' and status = 'FILLED' and account = '%s' and clientOrderId like '%s' " % (account, '%s%s' % (sellClientOrderId,'%'))
        #print sql
        cur.execute(sql)
        conn.commit()
        result = cur.fetchone()
        if result:
            return True
        cur.close()
        conn.close()
    except Exception as e:
        send_exception(traceback.format_exc())
    return False

# 更新 订单 上下架
def update_btc_binance_order_up(orderId, is_up):
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
        sql = "UPDATE `omni_btc_binance_order` SET `is_up` = '%s' WHERE orderId = '%s' " % (is_up, orderId)
        #print sql
        cur.execute(sql)
        conn.commit()
        result = cur.fetchall()
        return result
        cur.close()
        conn.close()
    except Exception as e:
        send_exception(traceback.format_exc())
    return False

# 插入 自动交易的日志表
def insert_btc_binance_order_auto_log(account, side, symbol, log_content):
    try:
        date = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        conn= MySQLdb.connect(
            host='127.0.0.1',
            port = 3306,
            user='omni_manage_pro',
            passwd='!omni123456manageMysql.pro',
            db ='z_omni_manage_pro',
        )
        cur = conn.cursor()
        cur.execute('set names utf8') #charset set code. it is not nessary now
        sql = "INSERT INTO `omni_btc_binance_order_auto_log` (`account`, `side`, `symbol`,`log_content`,`date`) VALUES ('%s', '%s', '%s',  '%s', '%s')" % (account, side, symbol, log_content.encode('utf-8'), date)
        cur.execute(sql)
        conn.commit()
        result = cur.fetchall()
        return result
        cur.close()
        conn.close()
    except Exception as e:
        #e_content =  json.dumps(traceback.format_exc().splitlines()).strip().replace('"','').replace("'",'')
        send_exception(traceback.format_exc())
    return False


# 查询当前是应该买还是麦
def find_btc_binance_order_buy_or_sell(account, symbol):
    try:
        conn= MySQLdb.connect(
            host='127.0.0.1',
            port = 3306,
            user='omni_manage_pro',
            passwd='!omni123456manageMysql.pro',
            db ='z_omni_manage_pro',
        )
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('set names utf8') #charset set code. it is not nessary now
        sql = "SELECT * FROM `omni_btc_binance_order`  WHERE is_up = '1' and account = '%s' and symbol = '%s' order by time desc " % (account, symbol)
        cur.execute(sql)
        conn.commit()
        result = cur.fetchone()
        return result
        cur.close()
        conn.close()
    except Exception as e:
        send_exception(traceback.format_exc())
    return False


# 查询最新的完成订单
def find_btc_binance_order_newest(account, symbol):
    try:
        conn= MySQLdb.connect(
            host='127.0.0.1',
            port = 3306,
            user='omni_manage_pro',
            passwd='!omni123456manageMysql.pro',
            db ='z_omni_manage_pro',
        )
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('set names utf8') #charset set code. it is not nessary now
        sql = "SELECT * FROM `omni_btc_binance_order`  WHERE (side = 'SELL' or side = 'BUY') and o_type in ('STOP_LOSS_LIMIT', 'TAKE_PROFIT_LIMIT') and is_auto = 1 and status = 'FILLED' and account = '%s' and symbol =  '%s' order by time desc " % (account, symbol)
        #print sql
        cur.execute(sql)
        conn.commit()
        result = cur.fetchone()
        if result:
            return result
        cur.close()
        conn.close()
    except Exception as e:
        send_exception(traceback.format_exc())
    return False

# 更新 订单 上下架
def update_btc_binance_reset_order_up(account, symbol, is_up):
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
        sql = "UPDATE `omni_btc_binance_order` SET `is_up` = '%s' WHERE account = '%s' and symbol = '%s' " % (is_up, account, symbol)
        #print sql
        cur.execute(sql)
        conn.commit()
        result = cur.fetchall()
        return result
        cur.close()
        conn.close()
    except Exception as e:
        send_exception(traceback.format_exc())
    return False



# 记录 最近交易的数据
def insert_binance_recent_trades_data_rate_test(account, buy_price, min_price, sell_price, max_price, qty, symbol, rate, confirm_rate, sync_time):
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
        sql = "INSERT INTO `omni_btc_binance_recent_trades_rate_test` (`account`, `buy_price`, `min_price`, `sell_price`, `max_price`, `qty`, `symbol`, `rate`, `confirm_rate`, `sync_time`) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (account, buy_price, min_price, sell_price, max_price, qty, symbol, rate, confirm_rate, sync_time)
        #print sql
        #sql = "INSERT INTO `ecs_t_marathon` (`name`, `start_run_time`) VALUES ('%s', '%s')" % (name, start_run_time)
        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        send_exception(traceback.format_exc())


