#encoding: utf-8
'''
获取淘宝联盟定向招商的宝贝信息
taobao.tbk.uatm.event.item.get
'''
from top.api.base import RestApi
class TbkUatmEventItemGetRequest(RestApi):
	def __init__(self,domain='gw.api.taobao.com',port=80):
		RestApi.__init__(self,domain, port)
		self.adzone_id = None
		self.event_id = None
		self.fields = None
		self.page_no = None
		self.page_size = None
		self.platform = None
		self.unid = None

	def getapiname(self):
		return 'taobao.tbk.uatm.event.item.get'
