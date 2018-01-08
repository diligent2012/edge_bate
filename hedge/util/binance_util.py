# coding=utf-8


import sys  
sys.path.append("..")
from binance_ref.client import Client
from binance_ref.exceptions import BinanceAPIException, BinanceRequestException, BinanceWithdrawException
import time
from binance_ref.enums import *

client = Client('ugXds1RBgjoc6n5WPtRyH2n9ahXw56bfLfFJJEW7cHqK2KzMZ3D1ZjhwhGBp455U', 'zQM8ci1whr3gych0WSQYA591zf5plZQlYBHHeDOJdpIQ1w2i9ug4v8pdqX57BvzU')


# 获取最近的交易（最多500）
def get_recent_trades(symbol='EOSBTC'):
    recent_trades = client.get_recent_trades(symbol = symbol)
    return recent_trades

        
def get_all_tickers():
    recent_trades = client.get_all_tickers()
    return recent_trades

def get_order_book(symbol='EOSBTC'):
    order_book = client.get_order_book(symbol = symbol)
    return order_book


def get_ticker(symbol='EOSBTC'):
    ticker = client.get_ticker(symbol = symbol)
    return ticker

def get_orderbook_tickers():
    orderbook_tickers = client.get_orderbook_tickers()
    return orderbook_tickers


def get_aggregate_trades(symbol='EOSBTC'):
    aggregate_trades = client.get_aggregate_trades(symbol = symbol)
    return aggregate_trades

# 限价单 买入
def order_limit_buy(symbol = 'EOSBTC', quantity = 1, price = 0.001):
    order_limit_buy_result = client.order_limit_buy(symbol = symbol, quantity = quantity, price = price)
    return order_limit_buy_result

# 限价单 卖出
def order_limit_sell(symbol = 'EOSBTC', quantity = 1, price = 0.001):
    order_limit_sell_result = client.order_limit_sell(symbol = symbol, quantity = quantity, price = price)
    return order_limit_sell_result

# 市价单 买入
def order_market_buy(symbol = 'EOSBTC', quantity = 1):
    order_market_buy_result = client.order_market_buy(symbol = symbol, quantity = quantity)
    return order_market_buy_result

# 市价单 卖出
def order_market_sell(symbol = 'EOSBTC', quantity = 1):
    order_market_sell_result = client.order_market_sell(symbol = symbol, quantity = quantity)
    return order_market_sell_result

def get_open_orders(symbol = 'EOSBTC'):
    open_orders = client.get_open_orders(symbol = symbol)
    return open_orders

def cancel_order(symbol , orderId):
    cancel_order = client.cancel_order(symbol = symbol, orderId = orderId)
    return cancel_order


def get_asset_balance(asset = 'EOS'):
    asset_balance = client.get_asset_balance(asset = asset)
    return asset_balance


def get_symbol_info(symbol = 'EOSBTC'):
    symbol_info = client.get_symbol_info(symbol = symbol)
    return symbol_info

