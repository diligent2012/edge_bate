# coding=utf-8
# 币安平台自动交易
# 

# 
# 
# 什么时候买呢 
# 比较当前买的价格,精确到5位数
# 然后降低1个百分点买,如果
# 
# 
# 什么时候卖
# 获取当前订单卖出的前3个的价格和数量

import sys,os
sys.path.append("../platform/")
sys.path.append("../util/")
from binance_ref.client import Client
from binance_ref.exceptions import BinanceAPIException, BinanceRequestException, BinanceWithdrawException
import time
from binance_ref.enums import *
from decimal import *

from db_util import insert_binance_recent_trades_data, insert_btc_binance_order, find_btc_binance_order_record
from binance_util import get_client, get_all_tickers, get_order_book, get_recent_trades, get_ticker, get_aggregate_trades, get_orderbook_tickers, get_open_orders,  get_asset_balance, cancel_order, get_symbol_info,get_all_orders, get_klines
from account_util import get_account_list
from helper_util import id_generator


# 代码执行针对订单有效时间
#LIMIT_DATE = '2018-01-07 00:00:00'

def start_trade_buy():
    account_list = get_account_list()
    for key,a_item in enumerate(account_list):
        client = get_client(a_item['api_key'], a_item['api_secret'])

        
        #获取所有订单
        all_orders = get_all_orders(client, 'EOSBTC');
        # 如果不为空
        if all_orders:
            for key,item in enumerate(all_orders):
                #print item
                #trade_time_ref = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(int(item['time'] / 1000)))
                #if (a_item['buy_limit_date'] < trade_time_ref and 'FILLED' == item['status']):
                    # if ('BUY' == item['side']):
                    #     account = a_item['account']
                    #     orderId = item['orderId']
                    #     price = item['price']
                    #     origQty = item['origQty']
                    #     trade_time = item['time']
                sellClientOrderId = id_generator()
                data = {}
                data['sellClientOrderId'] = sellClientOrderId
                data['account'] = a_item['account']
                data['orderId'] = item['orderId']
                data['clientOrderId'] = item['clientOrderId']
                data['origQty'] = item['origQty']
                data['icebergQty'] = item['icebergQty']
                data['symbol'] = item['symbol']
                data['side'] = item['side']
                data['timeInForce'] = item['timeInForce']
                data['status'] = item['status']
                data['stopPrice'] = item['stopPrice']
                data['time'] = item['time']
                data['isWorking'] = item['isWorking']
                data['o_type'] = item['type']
                data['price'] = item['price']
                data['executedQty'] = item['executedQty']
                btc_binance_order_record = find_btc_binance_order_record(item['orderId'])
                
                if not btc_binance_order_record:
                    insert_btc_binance_order(data)
          

def oper_is_sell(stop_sell_price, buy_price):
    (stop_sell_price - buy_price)/buy_price

    sell_rate = (Decimal(stop_sell_price) - Decimal(buy_price))/Decimal(buy_price)
    sell_rate = round(sell_rate,8)
    if(sell_rate >= 0.025):
        print sell_rate   
    else:
        print sell_rate


# 入口方法
def main():
    print "start : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    #start_trade_buy()
    oper_is_sell(0.00071541,0.00071)
    

if __name__ == '__main__':
    main() 