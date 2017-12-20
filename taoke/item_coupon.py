# -*- coding: utf-8 -*-
'''
Created on 2012-7-3

@author: lihao
'''
import top.api
import json

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
a = top.api.TbkDgItemCouponGetRequest()

'''
可以在运行期替换掉默认的appkey和secret的设置
a.set_app_info(top.appinfo("appkey","*******"))
'''
a.page_no = 1
a.page_size = 20
a.adzone_id = 117734916
a.platform = 2
a.q = "日系女袜子韩国秋冬款潮个性中筒韩版学院风纯棉女士长筒加厚保暖"

try:
    f= a.getResponse()
    print json.dumps(f);
    # for item in f['tbk_uatm_favorites_get_response']['results']['tbk_favorites']:
    #     print item['favorites_title']
except Exception,e:
    print(e)



    
