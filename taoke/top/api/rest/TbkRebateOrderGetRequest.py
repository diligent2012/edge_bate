#encoding: utf-8
from top.api.base import RestApi
class TbkRebateOrderGetRequest(RestApi):
    def __init__(self,domain='gw.api.taobao.com',port=80):
        RestApi.__init__(self,domain, port)
        self.span = None
        self.fields = None
        self.page_no = None
        self.page_size = None
        self.start_time = None

    def getapiname(self):
        return 'taobao.tbk.rebate.order.get'
