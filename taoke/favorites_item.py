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
a = top.api.TbkUatmFavoritesItemGetRequest()

'''
可以在运行期替换掉默认的appkey和secret的设置
a.set_app_info(top.appinfo("appkey","*******"))
'''

a.adzone_id = 117734916
a.favorites_id = 6890435

a.page_no = 1
a.page_size = 20
a.platform = 2
a.unid = 123
a.fields="num_iid,title,pict_url,small_images,reserve_price,zk_final_price,user_type,provcity,item_url,seller_id,volume,nick,shop_title,zk_final_price_wap,event_start_time,event_end_time,tk_rate,status,type"

try:
    f= a.getResponse()
    print(f)
    for item in f['tbk_uatm_favorites_item_get_response']['results']['uatm_tbk_item']:
        print item['item_url']
except Exception,e:
    print(e)



    
