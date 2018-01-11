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
from db_util import insert_binance_recent_trades_data, find_btc_binance_trade_buy, update_btc_binance_trade
from binance_util import get_client, get_all_tickers, get_order_book, create_order_limit_sell, get_recent_trades, get_ticker, get_aggregate_trades, get_orderbook_tickers, get_open_orders, get_asset_balance, cancel_order, get_symbol_info
from account_util import get_account_list

# ORDER_TYPE_LIMIT
# Limit order:限价订单。这个也容易理解，就是限定一个价格买入和卖出。比如某股票市价可能是15，你希望大跌后买入，你想设定10刀，这时候就用limit order，买入价格就是10刀。偶尔可能有一点点的不同，比如9.99这样。如果你是买入，实际买入价格应该和你设定的limit price一样或略低，如果你是卖出，实际卖出价格应该和你设定的limit price一样或略高，

# ORDER_TYPE_MARKET
# 市价订单。就是如果你下单后，基本上会马上执行的，该订单价格就是下单后的市场价格。

# ORDER_TYPE_STOP_LOSS
# 通常用来止损或者锁定利润。和limit order最大的差别是, Limit order在你下单后你的券商是马上将这个订单推送到市场。但是stop order不是，提交stop order后，这个订单在券商这里，拿下跌止损来说，比如当前股价是15，你希望如果股价下跌，最多损失5刀每股，你设定stop order price是10，只有当股票大跌的时候并且跌穿10刀的时候，这时候券商会将订单推向市场，成为一个market order, 以低于10刀的价格尽快卖出。但是券商无法保证卖出价格是多少。

# ORDER_TYPE_STOP_LOSS_LIMIT
# 可以这么理解stop order是一个trigger,触发条件， limit order是你严格限制的价格，券商只能按照你设置的limit price来买卖（可能会有微小差异，可以忽略）。所以stop limit order就是给你更多的控制权，你设定2个价格stop price和limit price，当达到stop price的时候，这时候这个stop limit order 就成为了一个limit order，接下来的行为和limit order一样了.比如你15买入一只股票，股票在下跌途中，你想在10刀止损，但是不想股票跌到10刀就马上止损，因为股票下跌过程中也是波动的，如果跌到10刀马上反弹了呢，止损止在最低点怎么办？你可以设定stop price，比如9.5刀，只有跌穿9.5刀后，然后才执行limit order。

# ORDER_TYPE_TAKE_PROFIT 
# ORDER_TYPE_TAKE_PROFIT_LIMIT
# ORDER_TYPE_LIMIT_MAKER


# 获取最近交易的订单平均价格和平均交易数量(10条) 暂时只做参考,没有用到
def get_history_trade_avg_data():
    recent_trades = get_recent_trades()
    all_price = 0.0
    all_qty = 0.0
    avg_price = 0.0
    avg_qty = 0.0
    for key,item in enumerate(recent_trades):
        if(key  >= len(recent_trades) - 10):
            #print item['price'], item['qty']
            #print float(item['price']), float(item['qty'])
            all_price += float(item['price'])
            all_qty += float(item['qty'])

    avg_price = round(all_price/10,8)
    avg_qty = round(all_qty/10)
    return avg_price, avg_qty



def get_curr_trade_price(client):

    # 总的利润率
    rate_total = 0.02

    # 买入参考交易数量
    buy_ref_data_count = 10

    # 卖出参考交易数量
    sell_ref_data_count = 10

    # 获取深度市场数据
    recent_trades = get_order_book(client)


    # 买入参考交易数量的 总价格
    buy_all_price = 0.0
    #buy_all_qty = 0.0

    # 买入参考交易数量的 平均价格
    buy_avg_price = 0.0
    #buy_avg_qty = 0.0

    # 卖出参考交易数量的 总价格
    sell_all_price = 0.0
    #sell_all_qty = 0.0
    
    # 卖出参考交易数量的 平均价格
    sell_avg_price = 0.0
    #sell_avg_qty = 0.0

    for key,item in enumerate(recent_trades['bids']):
        if (key < buy_ref_data_count):
            buy_all_price += float(item[0])
            #buy_all_qty += float(item[1])
    

    buy_avg_price =  buy_all_price / buy_ref_data_count
    #buy_avg_qty = buy_all_qty / buy_ref_data_count

    for key,item in enumerate(recent_trades['asks']):
        if (key < sell_ref_data_count):
            sell_all_price += float(item[0])
            #sell_all_qty += float(item[1])

    sell_avg_price =  sell_all_price / sell_ref_data_count
    #sell_avg_qty = sell_all_qty / sell_ref_data_count

    # 当前利润率
    rate = round( ((sell_avg_price - buy_avg_price) / buy_avg_price), 4)

    sell_rate = round((rate_total - rate) / round(float(3)/float(5),2), 4)
    buy_rate = round((rate_total - rate) / round(float(7)/float(5),2), 4)
    
    # 建议卖出价格
    sug_sell_price = round( sell_rate * sell_avg_price + sell_avg_price, 8)
    
    # 建议买入价格
    sug_buy_price = round( buy_avg_price - buy_rate * buy_avg_price, 8)

    #print round( (sell_avg_qty + buy_avg_qty) / 2)
    return sug_sell_price, sug_buy_price



# 卖出
def sell_order(last_sell_price, last_sell_qty = 20):
    order_limit_sell('EOSBTC', 1, 0.0005808);
    # 最终卖出价格
    last_sell_price = 0.0

# 获取24小时的平均价格
def get_24_avg_price(symbol = 'EOSBTC'):
    ticker = get_ticker()
    for key,item in enumerate(ticker):
        if (symbol == item['symbol']):
            # print item
            # print "最近成交价格:%s" % str(item['prevClosePrice']) 
            # print "最新价格:%s" % str(item['lastPrice'])
            # print "最低价格:%s" % str(item['lowPrice'])
            # print "价格变化:%s" % str(item['priceChange'])
            # print "开盘价格:%s" % str(item['openPrice'])
            # print "报价:%s" % str(item['bidPrice'])
            # print "加权平均价格:%s" % str(item['weightedAvgPrice'])
            # print "最高价格:%s" % str(item['highPrice'])
            # print "价格变化百分比:%s" % str(item['priceChangePercent'])
            # print "问价:%s" % str(item['askPrice'])
            return item['weightedAvgPrice']
            break

    return 0.0


def start_trade_sell():

    # 获取当前买入(还没有卖出的)的订单,准备卖出
    account_list = get_account_list()
    for key,a_item in enumerate(account_list):
        client = get_client(a_item['api_key'], a_item['api_secret'])
        
        sug_sell_price, sug_buy_price = get_curr_trade_price(client)
        print sug_sell_price, sug_buy_price
                
    
# 获取当前交易的最高价格
def get_curr_max_price(client):
    recent_trades = get_recent_trades(client)
    max_price = 0.0
    for key,item in enumerate(recent_trades):
        if(0 == key):
            max_price = item['price']
        else:
            if(item['price'] > max_price):
                max_price = item['price']
        
    return max_price  


def test():
    account_list = get_account_list()
    for key,a_item in enumerate(account_list):
        client = get_client(a_item['api_key'], a_item['api_secret'])

        ticker =  get_ticker(client)
        for key,item in enumerate(ticker):
            if ('EOSBTC' == item['symbol']):
                print item['askPrice']
                print item['lastPrice']
                print item['highPrice']
# 入口方法
def main():
    print "start : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    start_trade_sell()
    
    

if __name__ == '__main__':
    main() 