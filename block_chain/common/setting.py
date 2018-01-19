#!/usr/bin/python
#coding:utf-8
# OTCBTC 
# 所有全局设置

import sys  
sys.path.append("..")
import time



def get_otcbtc_symbols():
    SYMBOL_LIST = [
        {
            "symbol":"EOS" # EOS
        }
        ,
        {
            "symbol":"BTC" # 以太坊
        }
        ,
        {
            "symbol":"ETH" # 比特币
        }
    ]
    return SYMBOL_LIST

def get_binance_symbols():
    SYMBOL_LIST = [
        {
            "symbol":"EOSBTC" # EOS
        }
        ,
        {
            "symbol":"EOSETH" # 以太坊
        }
        ,
        {
            "symbol":"ETHBTC" # 比特币
        }
    ]
    return SYMBOL_LIST


# 所有账户
def get_account_list():

    ACCOUNT_LIST = [
        {
            "account":"changaiqing",
            "start_auto_date":"2018-01-17 00:00:00",
            "api_key":"ugXds1RBgjoc6n5WPtRyH2n9ahXw56bfLfFJJEW7cHqK2KzMZ3D1ZjhwhGBp455U",
            "api_secret":"zQM8ci1whr3gych0WSQYA591zf5plZQlYBHHeDOJdpIQ1w2i9ug4v8pdqX57BvzU",
            'qty': 10,
            "allow_symbol": [
                {
                    "symbol":"EOSBTC" # EOS
                }
            ]
        }
        ,
        {
            "account":"zhangchen",
            "start_auto_date":"2018-01-17 00:00:00",
            "api_key":"HYjjZgAEP7b68Egex3IoWGe9C9K3hUvpW0lhRKKJ3prnzAyOdaoaMvGudJgeX7oC",
            "api_secret":"I4SqDlfkVk6Y01UgXdwdG9720Pdc859xa4ShRKdo35GvVOVrvB1ceURx5zW8XiHH",
            'qty': 200,
            "allow_symbol": [
                {
                    "symbol":"EOSETH" # 以太坊
                }
               
            ]
        }
    ]
    return ACCOUNT_LIST

# 所有账户
def get_windfall_account_list():

    ACCOUNT_LIST = [
        {
            "account":"changaiqing",
            "start_auto_date":"2018-01-17 00:00:00",
            "api_key":"ugXds1RBgjoc6n5WPtRyH2n9ahXw56bfLfFJJEW7cHqK2KzMZ3D1ZjhwhGBp455U",
            "api_secret":"zQM8ci1whr3gych0WSQYA591zf5plZQlYBHHeDOJdpIQ1w2i9ug4v8pdqX57BvzU",
            'qty': 3,
            "allow_symbol": [
                {
                    "symbol":"EOSBTC" # EOS
                }
            ]
        }
    ]
    return ACCOUNT_LIST