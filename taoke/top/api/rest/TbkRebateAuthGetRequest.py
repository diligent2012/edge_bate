#encoding: utf-8
from top.api.base import RestApi
class TbkRebateAuthGetRequest(RestApi):
    def __init__(self,domain='gw.api.taobao.com',port=80):
        RestApi.__init__(self,domain, port)
        self.params = None
        self.fields = None
        self.type = None

    def getapiname(self):
        return 'taobao.tbk.rebate.auth.get'
