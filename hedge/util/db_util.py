#!/usr/bin/python
#coding:utf-8
import sys  
import sqlite3
import requests
import json
from bs4 import BeautifulSoup
import re
import MySQLdb
import time
import random


# 查询是否有正在买的订单
def find_btc_binance_order_buying(account):
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
        sql = "SELECT * FROM `omni_btc_binance_order`  WHERE side = 'BUY'  and status = 'NEW'  and account = '%s' order by time desc limit 1" % (account)
        #print sql
        cur.execute(sql)
        conn.commit()
        result = cur.fetchone()
        if result:
            return True
        cur.close()
        conn.close()
    except Exception as e:
        print e
    return False

# 查询是否有正在卖的订单
def find_btc_binance_order_selling(account):
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
        sql = "SELECT * FROM `omni_btc_binance_order`  WHERE side = 'SELL'  and status = 'NEW'  and account = '%s' order by time desc limit 1" % (account)
        #print sql
        cur.execute(sql)
        conn.commit()
        result = cur.fetchone()
        if result:
            return True
        cur.close()
        conn.close()
    except Exception as e:
        print e
    return False

# 获取最近一次卖出的交易数据
def find_btc_binance_order_sell_newest_one(account):
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
        sql = "SELECT * FROM `omni_btc_binance_order`  WHERE side = 'SELL'  and status = 'FILLED'  and account = '%s' order by time desc  limit 1" % (account)
        #print sql
        cur.execute(sql)
        conn.commit()
        result = cur.fetchone()
        return result
        cur.close()
        conn.close()
    except Exception as e:
        print e
    return False

# 查询买入时, 止盈设置纪录
def find_btc_binance_order_stop_buy_record_newest_one():
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
        sql = "SELECT * FROM `omni_btc_binance_order_stop_buy_record`  order by transactTime desc limit 1" 
        #print sql
        cur.execute(sql)
        conn.commit()
        result = cur.fetchone()
        return result
        cur.close()
        conn.close()
    except Exception as e:
        print e
    return False

# 插入 买入时, 止盈设置纪录
def insert_btc_binance_order_stop_buy_record(data):
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
        sql = "INSERT INTO `omni_btc_binance_order_stop_buy_record` (`orderId`,`clientOrderId`,`origQty`,`executedQty`,`symbol`,`side`,`timeInForce`,`status`,`stopPrice`,`transactTime`,`o_type`,`price`) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (orderId,clientOrderId,origQty,executedQty,symbol,side,timeInForce,status,stopPrice,transactTime,o_type,price)
        cur.execute(sql)
        conn.commit()
        result = cur.fetchall()
        return result
        cur.close()
        conn.close()
    except Exception as e:
        print e
    return False

# 获取上一次没有全部卖出的订单
def find_btc_binance_order_buy_newest_one_not_all_sell(account):
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
        sql = "SELECT * FROM `omni_btc_binance_order`  WHERE is_up = 1 and executedQty !=  0.00000000 and side = 'SELL'  and status = 'CANCELED'  and account = '%s' order by time desc  limit 1" % (account)
        #print sql
        cur.execute(sql)
        conn.commit()
        result = cur.fetchone()
        return result
        cur.close()
        conn.close()
    except Exception as e:
        print e
    return False

# 获取上一次买入的订单
def find_btc_binance_order_buy_newest_one(account):
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
        sql = "SELECT * FROM `omni_btc_binance_order`  WHERE is_up = 1 and side = 'BUY'  and status = 'FILLED'  and account = '%s' order by time desc  limit 1" % (account)
        #print sql
        cur.execute(sql)
        conn.commit()
        result = cur.fetchone()
        return result
        cur.close()
        conn.close()
    except Exception as e:
        print e
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
        sql = "SELECT * FROM `omni_btc_binance_order_stop_sell_record`  WHERE parentClientOrderId = '%s' order by transactTime desc limit 1" % (newClientOrderId)
        #print sql
        cur.execute(sql)
        conn.commit()
        result = cur.fetchone()
        return result
        cur.close()
        conn.close()
    except Exception as e:
        print e
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
        sql = "SELECT * FROM `omni_btc_binance_recent_trades_data` WHERE data_symbol = '%s' order by data_time desc limit 1" % (symbol)
        #print sql
        cur.execute(sql)
        conn.commit()
        result = cur.fetchall()
        return result
        cur.close()
        conn.close()
    except Exception as e:
        print e
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
        print e

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
        print e
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
        print e
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
        print e
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
        print e
    return False

# 查询是否有正在进行的订单
def find_btc_binance_order_is_up(account):
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
        sql = "SELECT * FROM `omni_btc_binance_order`  WHERE is_up = 1 and account = '%s' order by time desc limit 1" % (account)
        #print sql
        cur.execute(sql)
        conn.commit()
        result = cur.fetchone()
        if result:
            return True
        cur.close()
        conn.close()
    except Exception as e:
        print e
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
        print e
    return False

# 更新 订单 上下架
def update_btc_binance_order_up(orderId, is_up = 9):
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
        print e
    return False

#---------------------上面是重新整理------------------




def insert_binance_rate(sell_avg_price, buy_avg_price, rate, sync_time):
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
        sql = "INSERT INTO `omni_btc_binance_rate` (`sell_avg_price`, `buy_avg_price`, `rate`, `sync_time`) VALUES ('%s', '%s', '%s', '%s')" % (sell_avg_price, buy_avg_price, rate, sync_time)
        #sql = "INSERT INTO `ecs_t_marathon` (`name`, `start_run_time`) VALUES ('%s', '%s')" % (name, start_run_time)
        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print e

def find_btc_binance_order_oper_buy(account):
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
        sql = "SELECT * FROM `omni_btc_binance_order`  WHERE is_up = 1 and side = 'BUY' and account = '%s' " % (account)
        #print sql
        cur.execute(sql)
        conn.commit()
        result = cur.fetchall()
        return result
        cur.close()
        conn.close()
    except Exception as e:
        print e
    return False

def find_btc_binance_order_sell_record_surplus(account, sellClientOrderId):
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
        sql = "SELECT * FROM `omni_btc_binance_order`  WHERE side = 'SELL'  and account = '%s' and clientOrderId like '%s' " % (account, '%s%s' % (sellClientOrderId,'%'))
        #sql = "SELECT * FROM `omni_btc_binance_order`  WHERE side = 'SELL'  and account = '%s'  " % (account)
        #print sql
        cur.execute(sql)
        conn.commit()
        result = cur.fetchall()
        return result
        cur.close()
        conn.close()
    except Exception as e:
        print e
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
        print e
    return False

# 查询 最近交易
def find_btc_binance_recent_trades_data():
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
        sql = "SELECT * FROM `omni_btc_binance_recent_trades_data` order by transactTime desc " 
        #print sql
        cur.execute(sql)
        conn.commit()
        result = cur.fetchall()
        return result
        cur.close()
        conn.close()
    except Exception as e:
        print e
    return False


def find_btc_binance_trade_buy(account):
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
        sql = "SELECT * FROM `omni_btc_binance_trade_buy`  WHERE is_finish = 9  and account = '%s' " % (account)
        #print sql
        cur.execute(sql)
        conn.commit()
        result = cur.fetchall()
        return result
        cur.close()
        conn.close()
    except Exception as e:
        print e
    return False

# 插入 数据
def insert_btc_binance_trade_buy(account, buy_order_id, buy_price, buy_qty, buy_time, b_id):
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
        sql = "INSERT INTO `omni_btc_binance_trade_buy` (`account`, `buy_order_id`, `buy_price`, `buy_qty`, `buy_time`, `b_id`) VALUES ('%s', '%s', '%s', '%s', '%s', '%s')" % (account, buy_order_id, buy_price, buy_qty, buy_time, b_id)
        cur.execute(sql)
        conn.commit()
        result = cur.fetchall()
        return result
        cur.close()
        conn.close()
    except Exception as e:
        print e
    return False

# 更新数据 
def update_btc_binance_trade(b_id, sell_order_id, sell_price, sell_qty, sell_time):
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
        sql = "UPDATE `omni_btc_binance_trade` SET `sell_order_id` = '%s', `sell_price` = '%s', `sell_qty` = '%s', `sell_time` = '%s', `is_finish` = 1 WHERE b_id = '%s' " % (sell_order_id, sell_price, sell_qty, sell_time, b_id)
        #print sql
        cur.execute(sql)
        conn.commit()
        result = cur.fetchall()
        return result
        cur.close()
        conn.close()
    except Exception as e:
        print e
    return False

# 更新数据 
def update_btc_binance_trade_sell_order_id(b_id, sell_order_id):
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
        sql = "UPDATE `omni_btc_binance_trade` SET `sell_order_id` = '%s' WHERE b_id = '%s' " % (sell_order_id, b_id)
        #print sql
        cur.execute(sql)
        conn.commit()
        result = cur.fetchall()
        return result
        cur.close()
        conn.close()
    except Exception as e:
        print e
    return False

