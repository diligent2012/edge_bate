# coding=utf-8
# 获取binance(以下简称B)当前市场价格
# 获取huobi(以下简称H)当前市场价格
# 
# 第一种获取情况:
# 当B的市场价格 - H的市场价格 >  1%的时候
# 在B的市场卖出,同时在H的市场买入
# 
# 第二种获取情况:
# 当H的市场价格 - B的市场价格 >  1%的时候
# 在H的市场卖出,同时在B的市场买入
# 
# 第三种获取情况:
# 当B的市场卖出价格 - B的市场买入价格 >  1%的时候
# 在B的市场卖出价格卖出,同时在B的市场买入价格买入
# 
# 第四种获取情况:
# 当H的市场卖出价格 - H的市场买入价格 >  1%的时候
# 在H的市场卖出价格卖出,同时在H的市场买入价格买入
# 
# 
# 每成交一笔发送邮件或微信通知
# 
# 每天获取B的账户余额
# 每天获取H的账户余额

import sys  
sys.path.append("..")
from binance_ref.client import Client
from binance_ref.exceptions import BinanceAPIException, BinanceRequestException, BinanceWithdrawException
import time
from binance_ref.enums import *

from db_util import insert_binance_recent_trades_data

client = Client('ugXds1RBgjoc6n5WPtRyH2n9ahXw56bfLfFJJEW7cHqK2KzMZ3D1ZjhwhGBp455U', 'zQM8ci1whr3gych0WSQYA591zf5plZQlYBHHeDOJdpIQ1w2i9ug4v8pdqX57BvzU')

# 订单操作的币种
JOIN_ORDER_SYMBOL = [
    'EOSBTC',
    'EOSETH',
    'ETHBTC'
]


# ORDER_STATUS_NEW = 'NEW' // 新建
# ORDER_STATUS_PARTIALLY_FILLED = 'PARTIALLY_FILLED' // 部分填充
# ORDER_STATUS_FILLED = 'FILLED' // 填充
# ORDER_STATUS_CANCELED = 'CANCELED' // 取消
# ORDER_STATUS_PENDING_CANCEL = 'PENDING_CANCEL' // 等待取消
# ORDER_STATUS_REJECTED = 'REJECTED' // 拒绝
# ORDER_STATUS_EXPIRED = 'EXPIRED' // 过期


# ORDER_TYPE_LIMIT = 'LIMIT' // 限制
# ORDER_TYPE_MARKET = 'MARKET' // 市场
# ORDER_TYPE_STOP_LOSS = 'STOP_LOSS' // 止损
# ORDER_TYPE_STOP_LOSS_LIMIT = 'STOP_LOSS_LIMIT' //止损限额
# ORDER_TYPE_TAKE_PROFIT = 'TAKE_PROFIT' //获利
# ORDER_TYPE_TAKE_PROFIT_LIMIT = 'TAKE_PROFIT_LIMIT' // 获利限制
# ORDER_TYPE_LIMIT_MAKER = 'LIMIT_MAKER' //市场限额


# SIDE_BUY = 'BUY' // 买
# SIDE_SELL = 'SELL' // 卖

# TIME_IN_FORCE_GTC = 'GTC'
# TIME_IN_FORCE_IOC = 'IOC'
# TIME_IN_FORCE_FOK = 'FOK'

# ORDER_RESP_TYPE_ACK = 'ACK'
# ORDER_RESP_TYPE_RESULT = 'RESULT'
# ORDER_RESP_TYPE_FULL = 'FULL'





def get_all_order():
    my_trades = client.get_all_orders(symbol = 'EOSBTC')
    for key,item in enumerate(my_trades):
        print item
        print item['orderId'] # 订单ID
        # print item['clientOrderId']
        # print item['origQty']
        # print item['icebergQty']
        print item['symbol']
        # print item['side']
        # print item['timeInForce']
        # print item['status']
        # print item['stopPrice']
        # print item['time']
        # print item['isWorking']
        # print item['type']
        # print item['price']
        # print item['executedQty']
        if(ORDER_STATUS_NEW == item['status']):
            cancel_order(item['symbol'], item['orderId'])
        

def cancel_order(symbol, orderId):
    print symbol, orderId
    is_cancel = client.cancel_order(symbol=symbol, orderId=orderId)
    print is_cancel


def create_order(symbol = 'EOSBTC'):
    is_cancel = client.create_order(
            symbol=symbol, 
            side=SIDE_SELL, 
            type = ORDER_TYPE_LIMIT,
            timeInForce = TIME_IN_FORCE_GTC,
            quantity = 2,
            price ='0.00070000' 
            )


# 获取24小时报价
def get_ticker():
    tickers = client.get_ticker()
    for key,item in enumerate(tickers):
        print item
        
# 获取所有的价格
def get_all_tickers():
    all_tickers = client.get_all_tickers()
    for key,item in enumerate(all_tickers):
        #print item
        if("EOSBTC" == item['symbol']):
            print item['price'] 

def get_account():
    account = client.get_account()
    
    for key,item in enumerate(account['balances']):
        print item

# 获取最近的交易（最多500）
def get_recent_trades(symbol='EOSBTC'):
    recent_trades = client.get_recent_trades(symbol = symbol)
    for key,item in enumerate(recent_trades):
        
        isBuyerMaker = 0
        if (item['isBuyerMaker']):
            isBuyerMaker = 1

        isBestMatch = 0
        if (item['isBestMatch']):
            isBestMatch = 1

        insert_binance_recent_trades_data(isBuyerMaker, item['price'], item['qty'], item['time'], item['id'], isBestMatch)

def make_order():
    get_recent_trades()
    #get_all_order()

def oper_start():
    print "start : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    make_order()

def main():
    oper_start();

if __name__ == '__main__':
    main() 