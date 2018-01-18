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

#开始自动卖出
def start_auto_sell():
    try:
        # is_allow = allow_send_time()
        # if not is_allow:
        #     return
        account_list = get_account_list()
        for key,a_item in enumerate(account_list):
            client = Client(a_item['api_key'], a_item['api_secret'])
            account = a_item['account']
            qty = a_item['qty']
            start_auto_date = format_time_for_date(a_item['start_auto_date'])
            binance_symbols = a_item['allow_symbol']
            
            # 循环不同的币种
            for key,s_item in enumerate(binance_symbols): 
                symbol = s_item['symbol']

                oper_record_log = "10、执行开始卖出" + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

                oper_record_log += "\n20、账户: %s" % (account)

                oper_record_log += "\n30、币种: %s" % (symbol)

                # 同步账户下的订单
                oper_record_log = sync_all_order(client, account, symbol, start_auto_date, oper_record_log)

                # 查看是否有买入单子在进行
                is_buying_rst, oper_record_log = is_buying(account, symbol, oper_record_log)
                if(is_buying_rst):
                    break;

                # 获取上一次买入价格
                prev_buy_price, order_time, sellClientOrderId, oper_record_log = get_prev_buy_price(account, symbol, oper_record_log)

                # 获取当前最近的的交易中最高和最低价格
                min_price, max_price = get_recent_trade_max_min_price_by_trade_time(client, symbol, order_time)

                oper_record_log += "\n70、当前交易中价格: 最高价: %s 最低价: %s " % (str(max_price), str(min_price))

                if(prev_buy_price):
                    is_sell, oper_record_log = oper_is_sell(min_price, prev_buy_price, oper_record_log)
                    if (is_sell):

                        # 计算并获取 触发价格、止损价格 
                        sell_price, stop_sell_price, oper_record_log = oper_stop_sell_price(max_price, prev_buy_price, oper_record_log)
                        
                        if(0.0 != sell_price and 0.0 != stop_sell_price):

                            # 止损价格必须高于买入价格。兜底做法
                            is_secure = secure_check(stop_sell_price, prev_buy_price)
                            if (is_secure):
                                # 开始设置卖出止损
                                oper_record_log = set_stop_sell_price(client, sell_price, stop_sell_price, qty, symbol, sellClientOrderId, oper_record_log)
                else:
                    oper_record_log += "\n99、没有获取到上次买入,请重视"
                insert_btc_binance_order_auto_log(account, 'SELL', symbol, oper_record_log)        

    except Exception as e:
        send_exception(traceback.format_exc())

# 是否有买入在进行
def is_buying(account, symbol, oper_record_log):
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
        return True, oper_record_log
    return False, oper_record_log

def get_prev_buy_price(account, symbol, oper_record_log):
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
        return stopPrice, order_time, sellClientOrderId, oper_record_log
    return False, False, False, oper_record_log

# 最高价格是否大于买入价格的2.5%
def oper_is_sell(max_price, buy_price, oper_record_log):
    sell_rate = (Decimal(max_price) - Decimal(buy_price))/Decimal(buy_price)
    sell_rate = round(sell_rate,8)
    if(sell_rate >= 0.025):
        oper_record_log += "\n80-A、涨幅大于0.025: 最高价格: %s 买入价格: %s " % (str(max_price), str(buy_price))
        return True, oper_record_log
    oper_record_log += "\n80-B、涨幅小于0.025: 最高价格: %s 买入价格: %s " % (str(max_price), str(buy_price))
    return False, oper_record_log

# 开始设置止损价格
def oper_stop_sell_price(max_price, buy_price, oper_record_log):
    try:
        stop_rate = float(Decimal(1) - (Decimal(max_price) - Decimal(buy_price))/Decimal(buy_price) * Decimal(0.2))
        stop_sell_price = round(float(max_price) * stop_rate,8)
        sell_price = round(float(Decimal(stop_sell_price) * Decimal(1.0005)),8)
        oper_record_log += "\n80-C、得出的设置价格: 触发价格: %s 止损价格: %s " % (str(sell_price), str(stop_sell_price))
        return sell_price, stop_sell_price, oper_record_log
    except Exception as e:
        send_exception(traceback.format_exc())
    oper_record_log += "\n80-D、无法得出设置价格: 最高价格: %s 买入价格: %s " % (str(max_price), str(buy_price))
    return 0.0, 0.0, oper_record_log

# 开始设置止损价格
def set_stop_sell_price(client, sell_price, stop_sell_price, sell_qty, symbol, sellClientOrderId, oper_record_log):
    try:
        order_symbol = symbol
        order_side = SIDE_SELL
        order_type = ORDER_TYPE_STOP_LOSS_LIMIT
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
                oper_record_log += "\n90-C、和上次设置止损相同 设置币种: %s 设置交易数量: %s 设置交易触发价格: %s 设置交易止损价格: %s 设置买卖类型: %s 设置交易类型: %s 设置交易时区: %s " % (order_symbol, order_quantity, order_price, order_stopPrice, order_side, order_type, order_timeInForce)
            
            # 如果不相同,则取消订单 并重新设置
            else:
                oper_record_log += "\n90-B、重新设置止损 设置币种: %s 设置交易数量: %s 设置交易触发价格: %s 设置交易止损价格: %s 设置买卖类型: %s 设置交易类型: %s 设置交易时区: %s " % (order_symbol, order_quantity, order_price, order_stopPrice, order_side, order_type, order_timeInForce)
                cancel_order(client, order_symbol, orderId)
                sell_order_result = create_stop_sell_order(client, order_symbol, order_side, order_type, order_timeInForce, order_quantity, order_price, order_stopPrice, newSellClientOrderId)
                insert_btc_binance_order_stop_sell_record(sell_order_result, parentClientOrderId)
            
        # 第一次设置止损价格,触发价格、止损价格、数量
        else:
            oper_record_log += "\n90-A、第一次设置止损 设置币种: %s 设置交易数量: %s 设置交易触发价格: %s 设置交易止损价格: %s 设置买卖类型: %s 设置交易类型: %s 设置交易时区: %s " % (order_symbol, order_quantity, order_price, order_stopPrice, order_side, order_type, order_timeInForce)
            sell_order_result = create_stop_sell_order(client, order_symbol, order_side, order_type, order_timeInForce, order_quantity, order_price, order_stopPrice, newSellClientOrderId)
            insert_btc_binance_order_stop_sell_record(sell_order_result, parentClientOrderId)
       
    except Exception as e:
        send_exception(traceback.format_exc())
    finally:
        return oper_record_log
    return oper_record_log

def secure_check(stop_sell_price, prev_buy_price):
    if(stop_sell_price > prev_buy_price):
        return True
    return False

# 入口方法
def main():
    print "start : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    start_auto_sell()
    print "end : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

if __name__ == '__main__':
    main() 