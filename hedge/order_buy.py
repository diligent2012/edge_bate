# coding=utf-8

from binance_ref.client import Client
from binance_ref.exceptions import BinanceAPIException, BinanceRequestException, BinanceWithdrawException
import time
from binance_ref.enums import *

client = Client('ugXds1RBgjoc6n5WPtRyH2n9ahXw56bfLfFJJEW7cHqK2KzMZ3D1ZjhwhGBp455U', 'zQM8ci1whr3gych0WSQYA591zf5plZQlYBHHeDOJdpIQ1w2i9ug4v8pdqX57BvzU')


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


def test():

    #print client.get_account()
    #print client.ping() # 测试与Rest API的连接。

    #print client.get_server_time() # 测试与Rest API的连接性并获取当前的服务器时间。

    #print client.get_exchange_info() # 当前的交易所交易规则和符号信息

    #print client.get_order_book(symbol='BNBBTC')

    #print client.get_recent_trades(symbol='BNBBTC') # 获取最近的交易（最多500）

    #print client.get_historical_trades(symbol='BNBBTC') #获取历史交易

    #print client.get_aggregate_trades(symbol='BNBBTC')

    #print client.get_klines(symbol='EOSBTC', interval=KLINE_INTERVAL_30MINUTE)

    #depth = client.get_order_book(symbol='EOSBTC')
    #print depth

    #depth = client.get_order_book(symbol='ETHBTC')
    #print depth

    #depth = client.get_order_book(symbol='EOSETH')
    #print depth

    #products = client.get_products()
    #for key,item in enumerate(products['data']):
        #pass
        #print item

    my_trades = client.get_all_orders(symbol = 'EOSBTC')
    for key,item in enumerate(my_trades):
        print item['orderId'] # 订单ID
        print item['clientOrderId']
        print item['origQty']
        print item['icebergQty']
        print item['symbol']
        print item['side']
        print item['timeInForce']
        print item['status']
        print item['stopPrice']
        print item['time']
        print item['isWorking']
        print item['type']
        print item['price']
        print item['executedQty']



    
    # all_tickers = client.get_all_tickers()
    # for key,item in enumerate(all_tickers):
    #     #pass
    #     #print item['symbol']
    #     if("EOSBTC" == item['symbol']):
    #         print item['price'] 
            
    # order  = client.create_test_order(
    #     symbol = 'EOSBTC',
    #     side = SIDE_BUY,
    #     type = ORDER_TYPE_LIMIT,
    #     timeInForce = TIME_IN_FORCE_GTC,
    #     quantity = 100,
    #     price = '0.00001'
    #     )
    # print order

def crawl_start():
    print "start : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    test()

def main():
    crawl_start();

if __name__ == '__main__':
    main() 