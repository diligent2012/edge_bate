# coding=utf-8


import sys  
sys.path.append("..")
from binance_ref.client import Client
from binance_ref.exceptions import BinanceAPIException, BinanceRequestException, BinanceWithdrawException
import time
from binance_ref.enums import *



def get_client(api_key, api_secret):
    client = Client(api_key, api_secret)
    return client

#常爱卿
#client = Client('ugXds1RBgjoc6n5WPtRyH2n9ahXw56bfLfFJJEW7cHqK2KzMZ3D1ZjhwhGBp455U', 'zQM8ci1whr3gych0WSQYA591zf5plZQlYBHHeDOJdpIQ1w2i9ug4v8pdqX57BvzU')
#张诚
#client = Client('HYjjZgAEP7b68Egex3IoWGe9C9K3hUvpW0lhRKKJ3prnzAyOdaoaMvGudJgeX7oC', 'I4SqDlfkVk6Y01UgXdwdG9720Pdc859xa4ShRKdo35GvVOVrvB1ceURx5zW8XiHH')

# 获取最近的交易（最多500）
def get_recent_trades(client, symbol='EOSBTC'):
    recent_trades = client.get_recent_trades(symbol = symbol)
    return recent_trades

        
def get_all_tickers(client):
    recent_trades = client.get_all_tickers()
    return recent_trades

def get_order_book(client, symbol='EOSBTC'):
    order_book = client.get_order_book(symbol = symbol)
    return order_book


def get_ticker(client):
    ticker = client.get_ticker()
    return ticker

def get_orderbook_tickers(client):
    orderbook_tickers = client.get_orderbook_tickers()
    return orderbook_tickers


def get_aggregate_trades(client, symbol='EOSBTC'):
    aggregate_trades = client.get_aggregate_trades(symbol = symbol)
    return aggregate_trades


# 止损
def create_stop_order(client, symbol, side, o_type, timeInForce, quantity, price, stopPrice, newClientOrderId ):
    try:
        create_order_result = client.create_order(symbol = symbol, side = side, type = o_type, timeInForce = timeInForce, quantity = quantity, price = price, stopPrice = stopPrice, newClientOrderId = newClientOrderId)
        return create_order_result
    except BinanceAPIException as e:
        print(e.code)
        print(e.message)
    return False


def create_stop_buy_order(client, symbol, side, o_type, timeInForce, quantity, price, stopPrice):
    try:
        create_order_result = client.create_order(symbol = symbol, side = side, type = o_type, timeInForce = timeInForce, quantity = quantity, price = price, stopPrice = stopPrice)
        return create_order_result
    except BinanceAPIException as e:
        print(e.code)
        print(e.message)
    return False





# 限价单 买入
def order_limit_buy(client, symbol = 'EOSBTC', quantity = 1, price = 0.001):
    order_limit_buy_result = client.order_limit_buy(symbol = symbol, quantity = quantity, price = price)
    return order_limit_buy_result

# 限价单 卖出
def create_order_limit_sell(client, symbol, quantity, price, stopPrice, newClientOrderId ):
    order_limit_sell_result = client.order_limit_sell(symbol = symbol, quantity = quantity, price = price, stopPrice = stopPrice, newClientOrderId = newClientOrderId)
    return order_limit_sell_result

# 市价单 买入
def order_market_buy(client, symbol = 'EOSBTC', quantity = 1):
    order_market_buy_result = client.order_market_buy(symbol = symbol, quantity = quantity)
    return order_market_buy_result

# 市价单 卖出
def order_market_sell(client, symbol = 'EOSBTC', quantity = 1):
    order_market_sell_result = client.order_market_sell(symbol = symbol, quantity = quantity)
    return order_market_sell_result





def get_open_orders(client, symbol = 'EOSBTC'):
    open_orders = client.get_open_orders(symbol = symbol)
    return open_orders

def get_all_orders(client, symbol = 'EOSBTC'):
    all_orders = client.get_all_orders(symbol = symbol)
    return all_orders

def cancel_order(client, symbol , orderId):
    try:
        cancel_order = client.cancel_order(symbol = symbol, orderId = orderId)
        return cancel_order
    except BinanceAPIException as e:
        print(e.code)
        print(e.message)
    return False


def get_account(client):
    account = client.get_account()
    return account
    
def get_asset_balance(client, asset = 'EOS'):
    asset_balance = client.get_asset_balance(asset = asset)
    return asset_balance


def get_symbol_info(client, symbol = 'EOSBTC'):
    symbol_info = client.get_symbol_info(symbol = symbol)
    return symbol_info


def get_klines(client):
    klines = client.get_klines(symbol = "EOSBTC", interval=KLINE_INTERVAL_1MINUTE)
    return klines

