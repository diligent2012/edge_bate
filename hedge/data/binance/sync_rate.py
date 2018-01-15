# # coding=utf-8
# # 获取24小时报价

# import sys,os
# sys.path.append("../../platform/")
# sys.path.append("../../util/")
# from binance_ref.client import Client
# from binance_ref.exceptions import BinanceAPIException, BinanceRequestException, BinanceWithdrawException
# import time
# from binance_ref.enums import *

# from db_util import insert_binance_rate
# from binance_util import get_order_book


# def get_curr_trade_price():

#     # 总的利润率
#     #rate_total = 0.01

#     # 买入参考交易数量
#     buy_ref_data_count = 20

#     # 卖出参考交易数量
#     sell_ref_data_count = 20

#     # 获取深度市场数据
#     recent_trades = get_order_book()

#     # 买入参考交易数量的 总价格
#     buy_all_price = 0.0
#     #buy_all_qty = 0.0

#     # 买入参考交易数量的 平均价格
#     buy_avg_price = 0.0
#     #buy_avg_qty = 0.0

#     # 卖出参考交易数量的 总价格
#     sell_all_price = 0.0
#     #sell_all_qty = 0.0
    
#     # 卖出参考交易数量的 平均价格
#     sell_avg_price = 0.0
#     #sell_avg_qty = 0.0

#     for key,item in enumerate(recent_trades['bids']):
#         if (key < buy_ref_data_count):
#             buy_all_price += float(item[0])
#             #buy_all_qty += float(item[1])
    

#     buy_avg_price =  buy_all_price / buy_ref_data_count
#     #buy_avg_qty = buy_all_qty / buy_ref_data_count

#     for key,item in enumerate(recent_trades['asks']):
#         if (key < sell_ref_data_count):
#             sell_all_price += float(item[0])
#             #sell_all_qty += float(item[1])

#     sell_avg_price =  sell_all_price / sell_ref_data_count
#     #sell_avg_qty = sell_all_qty / sell_ref_data_count

#     # 当前利润率
#     rate = round( ((sell_avg_price - buy_avg_price) / buy_avg_price), 4)

#     # 建议卖出价格
#     #sug_sell_price = round( round((rate_total - rate) / 2, 4) * sell_avg_price + sell_avg_price, 8)
        
#     # 建议买入价格
#     #sug_buy_price = round( buy_avg_price - round((rate_total - rate) / 2, 4) * buy_avg_price, 8)

#     #print round( (sell_avg_qty + buy_avg_qty) / 2)
#     return sell_avg_price, buy_avg_price, rate

# # 入口方法
# def main():
#     print "start : " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
#     sell_avg_price, buy_avg_price, rate = get_curr_trade_price()
#     sync_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
#     insert_binance_rate(sell_avg_price, buy_avg_price, rate, sync_time)

# if __name__ == '__main__':
#     main() 