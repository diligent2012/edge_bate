# -*- coding: utf-8 -*-
# import top.api
 
# req=top.api.TbkRebateOrderGetRequest(url,port)
# req.set_app_info(top.appinfo(appkey,secret))
 
# req.fields="tb_trade_parent_id,tb_trade_id,num_iid,item_title,item_num,price,pay_price,seller_nick,seller_shop_title,commission,commission_rate,unid,create_time,earning_time"
# req.start_time="2015-03-05 13:52:08"
# req.span=600
# req.page_no=1
# req.page_size=20
# try:
#     resp= req.getResponse()
#     print(resp)
# except Exception,e:
#     print(e)






# -*- coding: utf-8 -*-
'''
Created on 2012-7-3

@author: lihao
'''
import top.api


'''
这边可以设置一个默认的appkey和secret，当然也可以不设置
注意：默认的只需要设置一次就可以了

'''
top.setDefaultAppInfo("24534684", "91f780f78b7f9a4277884eba77e2963b")

'''
使用自定义的域名和端口（测试沙箱环境使用）
a = top.api.UserGetRequest("gw.api.tbsandbox.com",80)

使用自定义的域名（测试沙箱环境使用）
a = top.api.UserGetRequest("gw.api.tbsandbox.com")

使用默认的配置（调用线上环境）
a = top.api.UserGetRequest()

'''
a = top.api.TbkRebateOrderGetRequest()

'''
可以在运行期替换掉默认的appkey和secret的设置
a.set_app_info(top.appinfo("appkey","*******"))
'''
# a.page_no = 1
# a.page_size = 20
# a.fields="favorites_title,favorites_id,type"

a.fields="tb_trade_parent_id,tb_trade_id,num_iid,item_title,item_num,price,pay_price,seller_nick,seller_shop_title,commission,commission_rate,unid,create_time,earning_time"
a.start_time="2017-03-05 13:52:08"
a.span=600
a.page_no=1
a.page_size=20

try:
    f= a.getResponse()
    print(f)
except Exception,e:
    print(e)



    
