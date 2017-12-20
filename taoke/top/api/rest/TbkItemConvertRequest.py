#encoding: utf-8
'''
淘宝客商品链接转换
taobao.tbk.item.convert
'''
from top.api.base import RestApi
class TbkItemConvertRequest(RestApi):
    def __init__(self,domain='gw.api.taobao.com',port=80):
        RestApi.__init__(self,domain, port)
        
        self.fields = None
        self.num_iids = None
        self.adzone_id = None
        self.platform  = None
        self.unid = None
        self.dx = None

    def getapiname(self):
        return 'taobao.tbk.item.convert'
