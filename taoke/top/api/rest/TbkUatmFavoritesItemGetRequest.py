#encoding: utf-8
'''
获取淘宝联盟选品库的宝贝信息
taobao.tbk.uatm.favorites.item.get
'''
from top.api.base import RestApi
class TbkUatmFavoritesItemGetRequest(RestApi):
	def __init__(self,domain='gw.api.taobao.com',port=80):
		RestApi.__init__(self,domain, port)
		self.adzone_id = None
		self.favorites_id = None
		self.fields = None
		self.page_no = None
		self.page_size = None
		self.platform = None
		self.unid = None

	def getapiname(self):
		return 'taobao.tbk.uatm.favorites.item.get'
