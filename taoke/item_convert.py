
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
a = top.api.TbkItemConvertRequest()

'''
可以在运行期替换掉默认的appkey和secret的设置
a.set_app_info(top.appinfo("appkey","*******"))
'''
a.fields="num_iid,click_url"
a.num_iids="123,456"
a.adzone_id=117734916
a.platform=2
a.unid="demo"
a.dx="1"

try:
    f= a.getResponse()
    print(f)
    
except Exception,e:
    print(e)



    
