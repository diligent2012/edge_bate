#encoding: utf-8
'''
淘宝客淘口令
taobao.tbk.tpwd.create
'''
from top.api.base import RestApi
class TbkTpwdCreateRequest(RestApi):
	def __init__(self,domain='gw.api.taobao.com',port=80):
		RestApi.__init__(self,domain, port)
		self.ext = None
		self.logo = None
		self.text = None
		self.url = None
		self.user_id = None

	def getapiname(self):
		return 'taobao.tbk.tpwd.create'
