#!/usr/bin/python
#coding:utf-8
# OTCBTC 
# 所有全局设置

import sys  
sys.path.append("..")
import time



def get_symbols():
    ACCOUNT_LIST = [
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
    return ACCOUNT_LIST