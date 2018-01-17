# coding=utf-8
# 币安平台自动交易
# 卖出

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

from setting import *
from db import *
from util import *
from helper import *

def start_sell():
        
    account_list = get_account_list()
    for key,a_item in enumerate(account_list):
        client = Client(a_item['api_key'], a_item['api_secret'])
        account = a_item['account']
        
        binance_symbols = a_item['allow_symbol']
        
        # 循环不同的币种
        for key,s_item in enumerate(binance_symbols): 
            symbol = s_item['symbol']

            oper_record_log = "执行开始卖出" + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

            oper_record_log += "\n账户: %s" % (account)

            oper_record_log += "\n币种: %s" % (symbol)

            # 同步账户下的订单
            oper_record_log = sync_all_order(client, account, symbol, oper_record_log)


            #当没有买入的时候,开始卖出
            is_buying_result = find_btc_binance_order_buying(account, symbol)
            if(is_buying_result):
                for key,buy_item in enumerate(is_buying_result): 
                    orderId = buy_item['orderId']
                    symbol = buy_item['symbol']
                    price = buy_item['price']
                    stopPrice = buy_item['stopPrice']
                    origQty = buy_item['origQty']
                    executedQty = buy_item['executedQty']
                    oper_record_log += "\n有买入订单进行中: 订单ID: %s 币种: %s  触发价格: %s 止损价格: %s 需要卖出数量: %s 实际卖出数量: %s" % (str(orderId), str(symbol), str(price), str(stopPrice), str(origQty), str(executedQty))
            else:

                # 获取上一次买入的订单
                order_buy_newest_one = find_btc_binance_order_buy_newest_one(account, symbol)

                if(order_buy_newest_one):
                    
                    order_time = int(order_buy_newest_one['time']) #上一次买入的时间
                    orderId = order_buy_newest_one['orderId'] #上一次买入的订单ID
                    symbol = order_buy_newest_one['symbol'] #上一次买入的币种
                    price = order_buy_newest_one['price'] #上一次买入的触发价格
                    stopPrice = order_buy_newest_one['stopPrice'] #上一次买入的止盈价格

                    origQty = order_buy_newest_one['origQty'] #上一次买入的数量
                    executedQty = order_buy_newest_one['executedQty'] #上一次买入的实际数量
                    sellClientOrderId = order_buy_newest_one['sellClientOrderId'] #上一次买入的客户端ID
                    
                    oper_record_log += "\n买入的数据: 订单ID: %s 币种: %s  触发价格: %s 止损价格: %s 需要卖出数量: %s 实际卖出数量: %s 卖出时间: %s" % (str(orderId), str(symbol), str(price), str(stopPrice), str(origQty), str(executedQty), format_time(order_time))

                    # 获取当前最近的的交易中最高和最低价格
                    min_price, max_price = get_recent_trade_max_min_price_by_trade_time(client, symbol, order_time)

                    oper_record_log += "\n当前交易中价格: 最高价: %s 最低价: %s " % (str(max_price), str(min_price))

                    # 当最近交易价格中 最高价格 高于 买入价格,大于2.5% 才进入卖出逻辑
                    is_sell = oper_is_sell(max_price, stopPrice)

                    oper_record_log += "\n价格比较结果: 是否可以卖出 %s 买入的价格: %s 最高价: %s " % (str(is_sell), str(stopPrice), str(max_price))

                    if (is_sell):

                        # 计算并获取 触发价格、止损价格 
                        sell_price, stop_sell_price = get_stop_sell_price_order(max_price, stopPrice)
                        
                        oper_record_log += "\n得出的设置价格: 触发价格: %s 止损价格 : %s " % (str(sell_price), str(stop_sell_price))

                        # 开始设置卖出止损
                        set_stop_sell_price_order(client, sell_price, stop_sell_price, origQty, symbol, sellClientOrderId)
                    else:
                        oper_record_log += "\n最高价格 低于 买入价格 2.5%: 最高价: %s 买入价格: %s " % (str(max_price), str(stopPrice))
                else:
                    #如果没有,提醒
                    oper_record_log += "\n获取不到上次买入数据,请知晓: 账户: %s 币种: %s " % (str(account), str(symbol))

            insert_btc_binance_order_auto_log(account, 'SELL', symbol, oper_record_log)        


        
# 最高价格是否大于买入价格的2.5%
def oper_is_sell(max_price, buy_price):
    sell_rate = (Decimal(max_price) - Decimal(buy_price))/Decimal(buy_price)
    sell_rate = round(sell_rate,8)
    if(sell_rate >= 0.025):
        return True
    return False

# 计算止损价格
def get_stop_sell_price_order(max_price, buy_price):
    stop_rate = float(Decimal(1) - (Decimal(max_price) - Decimal(buy_price))/Decimal(buy_price) * Decimal(0.05))
    stop_sell_price = round(float(max_price) * stop_rate,8)
    sell_price = round(float(Decimal(stop_sell_price) * Decimal(1.0005)),8)
    return sell_price, stop_sell_price


# 开始设置止损价格
def set_stop_sell_price_order(client, sell_price, stop_sell_price, sell_qty, symbol, sellClientOrderId):
    
    order_symbol = symbol
    order_side = SIDE_SELL
    order_type = ORDER_TYPE_TAKE_PROFIT_LIMIT
    order_timeInForce = TIME_IN_FORCE_GTC
    order_price = sell_price 
    order_stopPrice = stop_sell_price
    order_quantity = sell_qty
    
    # 对应买入的客户端ID
    parentClientOrderId = sellClientOrderId
    # 卖出的客户端ID
    newSellClientOrderId = '%s%s%s' % (sellClientOrderId,'66-66',str(int(time.time())))
    
    # 获取上一次设置的信息
    set_stop_sell_record_result = find_btc_binance_order_stop_sell_record_newest_one(parentClientOrderId)
    
    # 如果有设置,判断设置信息是否相同
    if(set_stop_sell_record_result):
        stopPrice = set_stop_sell_record_result['stopPrice'] # 上一次设置的止损价格
        price = set_stop_sell_record_result['price'] # 上一次设置的触发价格
        origQty = set_stop_sell_record_result['origQty'] # 上一次设置的数量
        orderId = set_stop_sell_record_result['orderId'] # 上一次设置的订单ID

        # 判断 触发价格、止损价格、购买数量是否相同; 如果相同,则不用设置;
        if( order_price == price and order_stopPrice == stopPrice and order_quantity == origQty):
            print "相同,不用设置"
        
        # 如果不相同,则取消订单 并重新设置
        else:
            print "重新设置止损"
            cancel_order(client, order_symbol, orderId)
            sell_order_result = create_stop_sell_order(client, order_symbol, order_side, order_type, order_timeInForce, order_quantity, order_price, order_stopPrice, newSellClientOrderId)
            insert_btc_binance_order_stop_sell_record(sell_order_result, parentClientOrderId)
        
    # 第一次设置止损价格,触发价格、止损价格、数量
    else:
        print "第一次设置"
        sell_order_result = create_stop_sell_order(client, order_symbol, order_side, order_type, order_timeInForce, order_quantity, order_price, order_stopPrice, newSellClientOrderId)
        insert_btc_binance_order_stop_sell_record(sell_order_result, parentClientOrderId)
       




# 入口方法
def main():
    print "start : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    start_sell()
    print "end : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

if __name__ == '__main__':
    main() 