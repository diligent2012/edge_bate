#encoding: utf-8
'''
淘宝客店铺关联推荐查询
taobao.tbk.shop.recommend.get
'''
from top.api.base import RestApi
class TbkShopRecommendGetRequest(RestApi):
	def __init__(self,domain='gw.api.taobao.com',port=80):
		RestApi.__init__(self,domain, port)
		self.count = None
		self.fields = None
		self.platform = None
		self.user_id = None

	def getapiname(self):
		return 'taobao.tbk.shop.recommend.get'
