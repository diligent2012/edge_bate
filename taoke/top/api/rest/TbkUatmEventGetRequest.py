#encoding: utf-8
'''
枚举正在进行中的定向招商的活动列表
taobao.tbk.uatm.event.get
'''
from top.api.base import RestApi
class TbkUatmEventGetRequest(RestApi):
	def __init__(self,domain='gw.api.taobao.com',port=80):
		RestApi.__init__(self,domain, port)
		self.fields = None
		self.page_no = None
		self.page_size = None

	def getapiname(self):
		return 'taobao.tbk.uatm.event.get'
