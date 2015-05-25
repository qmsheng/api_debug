#!/usr/bin/python
#-*- coding: UTF-8 -*- 

from django.template import loader,Context
from django.http import HttpResponse
from tools.models import modtools
from django.forms import *
from django.shortcuts import render_to_response, get_object_or_404, render
from django.http import HttpResponse,HttpResponseRedirect
from django import forms

import hashlib
import urllib
import urllib2
import httplib 

import sys
import json
import string

#coding:utf-8

# from django.views.decorators.csrf import csrf_exempt
# from django.views.decorators.csrf import requires_csrf_token

# appKey = '4223273916'
# secret = 'DA00D00CBFECD61E4EA4FA830FCEEA4C96C5683D'
# appKey = "184269830"
# secret = "931E498698AB2D9B1D93F419E572D2ACCA981488"

# appKey = "3862015082"
# secret = "5693BBB00ED6BE8A606A4D6A866DF8466DC70D10"


# KLD01 
# appKey = "3994652484"
# secret = "E4C9D76696927B1D964B451B031601E6539EA583"


# apiHost = "115.231.73.17"
# apiHost = "192.168.1.207"
# apiHost = "192.168.184.136"

# 点6
appKey = "2064302565"
secret = "BB9318B102E320C09B8AB9D5229B5668DB1C00D0"

#沙箱
# accountID = "SsYYnzgsdw"
# appKey = "3862015082"
# secret = "5693BBB00ED6BE8A606A4D6A866DF8466DC70D10"


api_server_list = {
	"jzs":"192.168.11.73",
	"debug":"192.168.1.207",
	"sendbox":"s9ct.mirrtalk.com",
	# production":"api.daoke.io",  #正式环境
}

ENVI_SERVER_LIST = (
	("jzs","jzs localhost"),
	("debug","线下调试"),
	("sendbox","沙箱环境"),
	# ("production","正式环境"),
)

api_post_list = {
	"jzs":80,
	"debug":80,
	"sendbox":80,
	"production":80,
}

api_remark_list = {
	"jzs":"jzs localhost",
	"debug":"线下调试",
	"sendbox":"沙箱环境",
	"production":"正式环境",
}

global_env_flag = ""

def my_urlencode(str) :
    reprStr = repr(str).replace(r'\x', '%')
    return reprStr[1:-1]

def http_post_api(req , url, data ,api_host , api_port ):
	tmp_api_host = ""
	tmp_api_port = 0

	if api_host != None and api_port != None :
		tmp_api_host = api_host
		tmp_api_port = api_port
	else:

		tmp_env_flag = req.session['environment']

		tmp_api_host = api_server_list[tmp_env_flag]
		tmp_api_port = api_post_list[tmp_env_flag]

	requrl = "http://{0}:{1}/{2}".format( tmp_api_host , tmp_api_port , url )

	print(requrl)


	try:
		headerdata = {"Host": tmp_api_host }
		conn = httplib.HTTPConnection(tmp_api_host,tmp_api_port)
		conn.request(method="POST",url = requrl, body = data, headers = headerdata) 

		# conn.request(method="POST",url = requrl, body = data ) 

		response = conn.getresponse()
		res= response.read()
		return res
	except:
	 	return  "http request failed : " +  requrl 

def dict_to_str(dict):
	return urllib.urlencode(dict)

def tuple_to_str(tuple):
	string = ""
	for k, v in enumerate(tuple):
		if len(string) == 0 :
			string = str(v[0]) + "=" + my_urlencode(str(v[1]))
		else:
			string = string + "&" + str(v[0]) + "=" + my_urlencode(str(v[1]))
	return string

def tuple_append(tuple):
	string = ""
	for k, v in enumerate(tuple):
		if len(string) == 0 :
			string = str(v[0]) + str(v[1])
		else:
			string = string + str(v[0]) + str(v[1])
	return string


def sortedDictValues(adict): 
	items = adict.items() 
	items.sort() 
	return [ (key, value) for key, value in items] 


def get_sign(dict, appkey_v , secret_v ):
	dict['appKey'] = appkey_v
	dict['secret'] = secret_v
	tuple = sortedDictValues(dict)
	tmp_str = tuple_append(tuple)
	print("really get sign:", tmp_str )
	sign = hashlib.sha1(tmp_str).hexdigest().upper()
	print( sign )
	del dict['secret']
	return sign


def templateApp(req, template_form,  uri , api_action , api_html = "apiform.html", api_host = None, api_port = None, before_sign = None, after_sign = None ):
	if req.method == 'POST':
		form = template_form(req.POST)
		dict = {} 
		for item in req.POST:
			dict[item] = req.POST[item].encode('utf-8')

		if before_sign != None:
			before_sign(dict)

		tmp_appkey = appKey
		tmp_secret = secret

		if req.session['appKey'] and req.session['secret']:
			tmp_appkey = req.session['appKey']
			tmp_secret = req.session['secret']

		dict['sign'] = get_sign(dict, tmp_appkey , tmp_secret)

		if after_sign != None:
			after_sign(dict)

		request_msg = dict_to_str(dict)

		result_msg = ""
		object_data = None

		try:
			result_msg = http_post_api(req , uri,request_msg, api_host, api_port )
			object_data = json.loads(result_msg)
		except :
			print result_msg
			pass

		return render_to_response(api_html, {'form':form, "api_action": api_action ,  "api_account": req.session['username'] , "uri": uri,  "request_msg":request_msg, "result_msg":result_msg, "object_data":object_data } )
	else:
		form = template_form()
		return render_to_response(api_html,{'form':form, "api_action": api_action , "api_account": req.session['username'] })



def templateApp_Debug(req, template_form,  uri , api_action , api_html = "apiform.html", api_host = None, api_port = None, before_sign = None, after_sign = None ):
	if req.method == 'POST':
		form = template_form(req.POST)
		for item in req.POST:
			dict[item] = req.POST[item].encode('utf-8')
			if item == "appKey":
				req.session['appKey'] = req['appKey']
			elif item == "secret":
				req.session['secret'] = req['secret']

		print(req.session['appKey'])
		print(req.session['secret'])

		return render_to_response(api_html, {'form':form, "api_action": api_action ,  "api_account": req.session['username'] , "uri": uri,  "request_msg":request_msg, "result_msg":result_msg, "object_data":object_data } )
	else:
		form = template_form()
		return render_to_response(api_html,{'form':form, "api_action": api_action , "api_account": req.session['username'] })


def templateApp_Login(req, template_form,  uri , api_action , api_html = "user_login.html", api_host = None, api_port = None, before_sign = None, after_sign = None ):
	if req.method == 'POST':
		form = template_form(req.POST)

		username = req.POST['accountID']
		environment = req.POST['environment']

		tmp_appKey = appKey 
		if req.POST['appKey']:
			tmp_appKey = req.POST['appKey'].strip()

		tmp_secret = secret
		if req.POST['secret']:
			tmp_secret = req.POST['secret'].strip()

		if username and len(username) == 10:
			req.session['username'] = username
			req.session['environment'] = environment
			if tmp_appKey != None and tmp_secret != None :
				req.session['appKey'] = tmp_appKey
				req.session['secret'] = tmp_secret
			return HttpResponseRedirect("index")
		else:
			result_msg = "accountID不正确"
			return render_to_response(api_html, {'form':form, "api_action": api_action , "result_msg":result_msg } )
	else:
		form = template_form()
		return render_to_response(api_html,{'form':form, "api_action": api_action  })




#=======================================login begin=========================================================================


class classUserLogin(forms.Form):
	appKey = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	secret = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	environment = forms.ChoiceField( choices = ENVI_SERVER_LIST, widget = forms.Select(attrs={'class':'form-control'} ) )
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )

def login(req):
	api_uri = ""
	return templateApp_Login(req, classUserLogin, api_uri , sys._getframe().f_code.co_name )

def logout(req):
	username = req.session.get('username')
	if username:
		del req.session['username']
	if req.session['environment']:
		del req.session['environment']

	if req.session['appKey']:
		del req.session['appKey']

	if req.session['secret']:
		del req.session['secret']

	return HttpResponseRedirect("login") 
		
def left(req):
	username = req.session.get('username')
	if username:
		return render_to_response('left.html', { 'username' : req.session['username'] } )
	else:
		return HttpResponseRedirect("login") 

def right(req):
	username = req.session.get('username')
	if username:
		return render_to_response('right.html', { 'username' : req.session['username'] } )
	else:
		return HttpResponseRedirect("login") 

def top(req):
	username = req.session.get('username')
	if username:

		tmp_env_flag = req.session['environment']
		server = api_remark_list[tmp_env_flag]
		host = api_server_list[tmp_env_flag] 
		port = api_post_list[tmp_env_flag]

		tmp_appkey = appKey 
		if req.session['appKey']:
			tmp_appkey = req.session['appKey']

		tmp_secret = secret 
		if req.session['secret']:
			tmp_secret = req.session['secret']

		return render_to_response('top.html', { 'username' : username , 'server' : server , "host" : host , "port" : port , "appkey":tmp_appkey ,"secret":tmp_secret } )
	else:
		return HttpResponseRedirect("login") 

def index(req):
	username = req.session.get('username')
	if username:
		return render_to_response('index.html', { 'username' : username  } )
	else:
		return HttpResponseRedirect("login") 
#-------------------------------login end--------------------------------------------------------------------




#---- 获取频道类型 
FETCH_SECRET_INFO_TYPE = (
	('1', '1--群聊频道广场'),
	('2', '2--已创建的频道'),
	('3', '3--已加入的频道'),
	('4', '4--等待验证/驳回的频道')
)

#---- 频道类别
SECRET_CATALOG_LIST = (
	('','----全部'),
	('100101','100101--同事朋友'),
	('100102','100102--车友会'),
	('100103','100103--同城交友'),
	('100104','100104--兴趣爱好'),
	('100105','100105--行业交流'),
	('100106','100106--吃喝玩乐'),
	('100107','100107--品牌产品'),
	('100108','100108--线下服务'),
	('100109','100109--交通出行'),
	('100110','100110--应急救援'),
	('100111','100111--两性情感'),
	('300001', '300001--的哥'),
	('300002' ,'300002--汽车'),
	('300003' ,'300003--星座'),
	('300004' ,'300004--地区'),
	('300005' ,'300005--电影'),
	('300006' ,'300006--闲谈'),
	('300007' ,'300007--搞笑'),
	('300008' ,'300008--旅行')

)
#--微频道
MIC__CATALOG_LIST = (
	('','----全部'),
	('100101','100101--同事朋友'),
	('100102','100102--车友会'),
	('100103','100103--同城交友'),
	('100104','100104--兴趣爱好'),
	('100105','100105--行业交流'),
	('100106','100106--吃喝玩乐'),
	('100107','100107--品牌产品'),
	('100108','100108--线下服务'),
	('100109','100109--交通出行'),
	('100110','100110--应急救援'),
	('100111','100111--两性情感'),
	('200001','200001--节操几个钱'),
	('200002','200002--美女要不要'),
	('200003','200003--大叔也疯狂'),
	('200004','200004--鲜肉来两斤'),
	('200005','200005--旅行约一约'),
	('200006','200006--两性深夜谈'),
	('200007','200007--美食胖子送'),
	('200008','200008--搞基自由')

)

JOIN_CHANNEL_STATUS = (
	('0','0--等待验证的频道'),
	('2','2--管理员拒绝的频道'),
)


#---- 群聊频道开放类型
SECRET_OPENTYPE = (
	('0','0--非公开'),
	('1','1--公开'),
)

#---- 群聊频道加入类型
SECRET_VERITY_TYPE = (
	('0','0--加入不需要验证'),
	('1','1--加入需求验证'),
)

#---- 群聊频道审核类型
SECRET_CHECKSTATUS_TYPE = (
	('1','1--通过'),
	('2','2--拒绝'),
)
#---- 获取用户状态
SECRET_USER_STATUS = (
	('1','1--正常'),
	('2','2--禁言'),
	('3','3--拉黑')

)
#---- 设置关联键
SECRET_USERKEY = (
	('4','4--+键'),
	('5','5--++键')

)

#---- 管理频道类型
MANAGE_SECRET_TYPE = (
	('1','1--公司管理频道(curStatus  2 关闭频道)'),
	('2','2--管理员管理频道(curStatus 1-正常 / 2-禁言用户/3-拉黑用户)')
)

#---- 按键类型
SECRET_CUSTOMTYPE = (
	('2','2--customType:2(actionType:5)'),
	('6','6--customType:6(actionType:4)')
)

#得到在线列表
FETCH_SECRET_ONLINE_INFO = (
	('','可不传，自动识别普通用户或管理员'),
	('1','1--管理员得到在线列表'),
	('2','2--普通用户得到在线列表')
)

#频道类型
GET_CHANNEL_TYPE = (

	('1','1--主播频道'),
	('2','2--群聊频道')
)
#====================MicroChannel==========
#频道状态
MICROCHANNEL_STATUS = (
	('0','0--未审核'),
	('1','1--驳回'),
	('2','2--成功')
)
#查询频道类型
FETCH_MICRO_TYPE = (
	('0','0--公司查询频道'),
	('1','1--频道管理员查询频道'),
	('2','2--普通用户查询频道')

 )
#修改微频道/被驳回的频道
MODIFY_CHANNEL_TYPE = (
	('1','1--修改未通过的频道微'),
	('2','2--修改已通过的频道微')
)

FOLLOW_CHANNEL_TYPE = (
	('1',"1--关注频道"),
	('2',"2--解散频道")
)
#================MIC END===================


#================OAUTH BEGIN===============

#第三方开发者类型
DEVELOPER_TYPE = (
	('0','0--语镜用户'),
	('1','1--外部个人用户'),
	('2','2--外部企业用户')
)

#设置开发者审核状态
DEVELOPER_STATUS = (
	('0','0--审核中'),
	('1','1--审核通过'),
	('2','2--无开发权限')
)

#设置第三方应用审核状态
THIRD_PARTY_APP_STATUS = (
	('0','0--审核中'),
	('1','1--审核通过'),
	('2','2--审核未通过')
)

#获取开发者审核状态
GET_DEVELOPER_TYPE = (
	('','所有'),
	('0','0--审核中'),
	('1','1--审核通过'),
	('2','2--无开发权限')
)

#获取开发者的第三方应用
VALIDITY_TYPE = (
	('','所有'),
	('0','0--无效'),
	('1','1--有效'),
)

#设置APP频率控制FreqType
OAUTH_FREQUENCY_TYPE = (
	('','暂时支持第一种'),
	('1','1--每小时/每天/每月/每年'),
	('2','2--包年/包月'),
)

#暂不支持
OAUTH_NOT_SUPPORT_NOW = (
	('','暂时不支持'),
)

#设置APP频率控制customType
OAUTH_CUSTOM_TYPE = (
	('1','1--每年'),
	('2','2--每月'),
	('3','3--每天'),
	('4','4--每小时'),
)


#OAUTH第三方开发者类型(对应appKeyInfo)
#1:内部用户,2:企业用户,3:个人用户,4:合同用户
OAUTH_DEVELOPER_TYPE = (
	('1','1--内部用户'),
	('2','2--企业用户'),
	('3','3--个人用户(需要accountID)'),
	('4','4--合同用户'),
)

#===============OAUTH END=====================

#===============REWARD BEGIN==================

REWARD_RETURN_TYPE =  (
	('1','1--个人'),
	('2','2--企业'),
	('3','3--混合'),
)

REWARD_PARENT_ID = (
	('0','0--否'),
	('1','1--是'),
)

REWARD_IS_CHANNEL = (
	('0','0--否'),
	('1','1--是'),
)

REWARD_ALLOW_EXCHANGE = (
	('0','0--不允许'),
	('1','1--允许'),	
)

REWARD_BONUS_TYPE = (
	('0','0--无奖金'),
	('1','1--密点'),	
	('2','2--微点'),
	('4','4--其它方式'),
)

REWARD_SHARE_INFO = (
	('0','0--不分享'),
	('1','1--分享'),
)

REWARD_BONUS_RETURN_TARGET_TYPE = (
	('1','1--个人'),
	('2','2--个人与企业,个人优先'),	
	('3','3--个人与企业,企业优先'),
	('4','4--企业'),
)

#isAnonymous
#0代表不匿名,1代表匿名
REWARD_IS_ANONYMOUS =  (
	('0','0--不匿名'),
	('1','1--匿名'),
)

#donatedType
#1为金钱,2为里程
REWARD_DONATED_TYPE = (
	('1','1--金钱'),
	('2','2--里程'),
)

#regularDonation
#0为否,1为每月自动捐赠,2每季度自动捐赠,3每年自动捐赠
REWARD_REGULAR_DONATION = (
	('0','0--否'),
	('1','1--每月自动捐赠'),
	('2','2--每季自动捐赠'),
	('3','3--每年自动捐赠'),
)

#type
#排名类型１代表日排名，２代表周排名，３代表月>排名，４代表总排名(若type为４则time可以不传)
REWARD_TYPE = (
	('1','1--日排名'),
	('2','2--周排名'),
	('3','3--月排名'),
	('4','4--总排名'),
)

#withdrawType
#1:支付宝提现,2:手机话费充值,3:企业帐户提现(目前只能为1,2,3)
REWARD_WITHDRAW_TYPE = (
	('1','1--支付宝提现'),
	('2','2--手机话费充值'),
	('3','3--企业帐户提现'),
)

#withdrawAccountType
#1代表支付宝提现,2代表手机话费充值(目前只能为1,2)
REWARD_WITHDRAW_ACCOUNT_TYPE = (
	('1','1--支付宝提现'),
	('2','2--手机话费充值'),
)

#showType
#展示类型(默认为1，表示显示给普通用户查看，2表示显示给高级用户)
REWARD_WITHDRAW_ACCOUNT_TYPE = (
	('1','1--显示给普通用户'),
	('2','2--显示给高级用户'),
)

#moneyType
#1：获取密点类型，空：实际金额(其他报错)
REWARD_WITHDRAW_ACCOUNT_TYPE = (
	('1','1--获取密点类型'),
	('','空--实际金额'),
)

#消息类型
SECRET_MESSAGE_TYPE = (
	('','----全部消息'),
	('0','0----未处理'),
	('1','1----同意'),
	('2','2----拒绝'),
)

#===============REWARD END====================




class classApplySecretChannel(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' }) , label = "accountID" ) 
	channelName = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	channelIntroduction = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	channelCityCode = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})   )
	channelCatalogID = forms.ChoiceField( choices = SECRET_CATALOG_LIST, widget = forms.Select(attrs={'class':'form-control'} ) )
	channelCatalogUrl = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	openType = forms.ChoiceField( choices = SECRET_OPENTYPE , widget = forms.Select(attrs={'class':'form-control'})  )
	isVerity = forms.ChoiceField( choices = SECRET_VERITY_TYPE ,  widget=forms.Select(attrs={'class':'form-control'})  )
	channelKeyWords = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )

def applySecretChannel(req):
	api_uri = "clientcustom/v2/applySecretChannel"
	return templateApp(req, classApplySecretChannel, api_uri , sys._getframe().f_code.co_name)


class classModifySecretChannelInfo(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' }) , label = "accountID" ) 
	channelName = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	channelNumber = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	channelOpenType = forms.ChoiceField( choices = SECRET_OPENTYPE , widget = forms.Select(attrs={'class':'form-control'})  )
	channelIntro = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})   )
	channelCatalogID = forms.ChoiceField( choices = SECRET_CATALOG_LIST, widget = forms.Select(attrs={'class':'form-control'} ) )
	channelLogoUrl = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	channelCitycode = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})   )
	channelKeyWords = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )

def modifySecretChannelInfo(req):
	api_uri = "clientcustom/v2/modifySecretChannelInfo"
	return templateApp(req, classModifySecretChannelInfo, api_uri , sys._getframe().f_code.co_name)




class classManageSecretChannelUsers(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' }) , label = "accountID" ) 
	channelNumber = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	infoType = forms.ChoiceField(choices=MANAGE_SECRET_TYPE  , widget = forms.Select(attrs={'class':'form-control'}   ) )
	userAccountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' })  ) 
	curStatus = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )

def manageSecretChannelUsers(req):
	api_uri = "clientcustom/v2/manageSecretChannelUsers"
	return templateApp(req, classManageSecretChannelUsers, api_uri , sys._getframe().f_code.co_name)


# class classSetCustomInfo(forms.Form):
# 	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' }) , label = "accountID" ) 
# 	actionType = forms.ChoiceField( choices = SECRET_USERKEY,  widget=forms.Select(attrs={'class':'form-control'} ) )
# 	customType = forms.ChoiceField( choices = SECRET_CUSTOMTYPE, widget=forms.Select(attrs={'class':'form-control' })  ) 
# 	customParameter = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' })  ) 

# def setCustomInfo(req):
# 	api_uri = "clientcustom/v2/setCustomInfo"
# 	return templateApp(req, classSetCustomInfo, api_uri , sys._getframe().f_code.co_name)





class classFetchSecretChannel(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" ) 
	channelName = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'} ) )
	channelNumber = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'} ))
	cityCode = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'} ))
	status = forms.ChoiceField(choices=JOIN_CHANNEL_STATUS  , widget = forms.Select(attrs={'class':'form-control'}   ) )
	catalogID = forms.ChoiceField( choices = SECRET_CATALOG_LIST, widget = forms.Select(attrs={'class':'form-control'} ) )
	infoType = forms.ChoiceField(choices=FETCH_SECRET_INFO_TYPE  , widget = forms.Select(attrs={'class':'form-control'}   ) )
	startPage = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' , 'value':"1" } ))
	pageCount = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' , 'value':"20" } ))


def fetchSecretChannel(req):
	api_uri = "clientcustom/v2/fetchSecretChannel"
	return templateApp(req, classFetchSecretChannel, api_uri , sys._getframe().f_code.co_name)


class classSecretMessage(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" ) 
	status = forms.ChoiceField(choices=SECRET_MESSAGE_TYPE  , widget = forms.Select(attrs={'class':'form-control'}   ) )
	startPage = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' , 'value':"1" } ))
	pageCount = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' , 'value':"20" } ))


def secretChannelMessage(req):
	api_uri = "clientcustom/v2/secretChannelMessage"
	return templateApp(req, classSecretMessage, api_uri , sys._getframe().f_code.co_name)



class classGetCustomInfo(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" ) 
	actionType = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' , 'value':"4" } ))


def getCustomInfo(req):
	api_uri = "clientcustom/v2/getCustomInfo"
	return templateApp(req, classGetCustomInfo, api_uri , sys._getframe().f_code.co_name)



class classVeritySecretChannelMessage(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" ) 
	applyAccountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'} ) )
	applyAccountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'} ) )
	checkRemark = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'} ) )
	checkStatus = forms.ChoiceField( choices = SECRET_CHECKSTATUS_TYPE,  widget=forms.Select(attrs={'class':'form-control'} ) )
	applyIdx = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'} ) )


def veritySecretChannelMessage(req):
	api_uri = "clientcustom/v2/veritySecretChannelMessage"
	return templateApp(req, classVeritySecretChannelMessage, api_uri , sys._getframe().f_code.co_name)


class classJoinSecretChannel(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" ) 
	uniqueCode = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	remark  = forms.CharField( max_length = "120", widget=forms.TextInput(attrs={'class':'form-control'} ))


def joinSecretChannel(req):
	api_uri = "clientcustom/v2/joinSecretChannel"
	return templateApp(req, classJoinSecretChannel, api_uri , sys._getframe().f_code.co_name)


class classGetSecretChannelInfo(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" ) 
	channelNumber = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def getSecretChannelInfo(req):
	api_uri = "clientcustom/v2/getSecretChannelInfo"
	return templateApp(req, classGetSecretChannelInfo, api_uri , sys._getframe().f_code.co_name)

class classGetUserJoinListSecretChannel(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" ) 
	channelNumber = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	infoType = forms.ChoiceField( choices = FETCH_SECRET_ONLINE_INFO, widget = forms.Select(attrs={'class':'form-control'} ) )
	startPage = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' , 'value':"1" } ))
	pageCount = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' , 'value':"20" } ))

def getUserJoinListSecretChannel(req):
	api_uri = "clientcustom/v2/getUserJoinListSecretChannel"
	return templateApp(req, classGetUserJoinListSecretChannel, api_uri , sys._getframe().f_code.co_name)


class classQuitSecretChannel(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" ) 
	channelNumber = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def quitSecretChannel(req):
	api_uri = "clientcustom/v2/quitSecretChannel"
	return templateApp(req, classQuitSecretChannel, api_uri , sys._getframe().f_code.co_name)




class classGetCatalogInfo(forms.Form):
	channelType = forms.ChoiceField( choices = GET_CHANNEL_TYPE, widget = forms.Select(attrs={'class':'form-control'}))
	startPage = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' ,  'value':"1" } ))
	pageCount = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' ,  'value':"20"} ))

def getCatalogInfo(req):
	api_uri = "clientcustom/v2/getCatalogInfo"
	return templateApp(req, classGetCatalogInfo, api_uri , sys._getframe().f_code.co_name)




#=====================================主播频道 begin==========================================

class classApplyMicroChannel(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' }) , label = "accountID" ) 
	channelNumber = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	channelName = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	channelIntroduction = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	channelCityCode = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})   )
	channelCatalogID = forms.ChoiceField( choices = MIC__CATALOG_LIST, widget = forms.Select(attrs={'class':'form-control'} ) )
	channelCatalogUrl = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	chiefAnnouncerIntr = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	channelKeyWords = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )

def applyMicroChannel(req):
	api_uri = "clientcustom/v2/applyMicroChannel"
	return templateApp(req, classApplyMicroChannel, api_uri , sys._getframe().f_code.co_name)

class classCheckApplyMicroChannel(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' }) , label = "accountID" )
	checkAccountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' }) ) 
	channelNumber = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	checkRemark = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	checkStatus = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	channelRemark = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})   )
	applyIdx = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})   )
	channelKeyWords = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )

def checkApplyMicroChannel(req):
	api_uri = "clientcustom/v2/checkApplyMicroChannel"
	return templateApp(req, classCheckApplyMicroChannel, api_uri , sys._getframe().f_code.co_name)



class classFetchMicroChannel(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' }) , label = "accountID" )
	channelStatus = forms.ChoiceField( choices = MICROCHANNEL_STATUS, widget = forms.Select(attrs={'class':'form-control'} ) )
	cityCode = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	catalogID = forms.ChoiceField( choices = MIC__CATALOG_LIST, widget = forms.Select(attrs={'class':'form-control'} ) )
	channelName = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	channelNumber = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})   )
	channelKeyWords = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})   )
	startPage = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control','value':"1"})  )
	pageCount = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control','value':'20'})  )
	infoType = forms.ChoiceField( choices = FETCH_MICRO_TYPE, widget = forms.Select(attrs={'class':'form-control'} ) )

def fetchMicroChannel(req):
	api_uri = "clientcustom/v2/fetchMicroChannel"
	return templateApp(req, classFetchMicroChannel, api_uri , sys._getframe().f_code.co_name)


class classGetMicroChannelInfo(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' }) , label = "accountID" )
	channelNumber = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})   )


def getMicroChannelInfo (req):
	api_uri = "clientcustom/v2/getMicroChannelInfo "
	return templateApp(req, classGetMicroChannelInfo, api_uri , sys._getframe().f_code.co_name)

class classModifyMicroChannel(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' }) , label = "accountID" )
	channelCityCode = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	channelCatalogID = forms.ChoiceField( choices = MIC__CATALOG_LIST, widget = forms.Select(attrs={'class':'form-control'} ) )
	channelName = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	channelNumber = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})   )
	channelKeyWords = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})   )
	infoType = forms.ChoiceField( choices = MODIFY_CHANNEL_TYPE, widget = forms.Select(attrs={'class':'form-control'} ) )
	channelIntroduction = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})   )
	beforeChannelNumber = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})   )
	chiefAnnouncerIntr = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})   )
	channelCatalogUrl = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})   )


def modifyMicroChannel(req):
	api_uri = "clientcustom/v2/modifyMicroChannel"
	return templateApp(req, classModifyMicroChannel, api_uri , sys._getframe().f_code.co_name)


class classFollowMicroChannel(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' }) , label = "accountID" )
	channelNumber = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})   )
	uniqueCode 	= forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})   )
	followType =  forms.ChoiceField( choices = FOLLOW_CHANNEL_TYPE, widget = forms.Select(attrs={'class':'form-control'} ) )



def followMicroChannel  (req):
	api_uri = "clientcustom/v2/followMicroChannel"
	return templateApp(req, classFollowMicroChannel, api_uri , sys._getframe().f_code.co_name)

# 批量关注微频道 2015-05-21 
class classBatchFollowMicroChannel(forms.Form):
	uniqueCode = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "邀请码"   )
	totalList = forms.CharField( widget=forms.Textarea(attrs={'class':'form-control'}) , label = "用户列表,使用逗号分隔"  )

def batchFollowMicroChannel(req):
	api_uri = "clientcustom/v2/batchFollowMicroChannel"
	return templateApp(req, classBatchFollowMicroChannel, api_uri , sys._getframe().f_code.co_name)

# 批量关注微频道 2015-05-21 

class classGetBossFollowList(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' }) , label = "accountID" )
	channelNumber = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})   )
	startPage 	= forms.CharField( widget=forms.TextInput(attrs={'class':'form-control','value':"1"})   )
	pageCount =  forms.CharField( widget=forms.TextInput(attrs={'class':'form-control','value':"20"})   )



def getBossFollowListMicroChannel(req):
	api_uri = "clientcustom/v2/getBossFollowListMicroChannel"
	return templateApp(req, classGetBossFollowList, api_uri , sys._getframe().f_code.co_name)




#===========================主播频道 end========================================================






#=====================================道客账户 begin======================================================

def add_custom_before_sign(dict):
	if dict['accountType'] == "1":
		del dict['mobile']
		del dict['userEmail']
	elif dict['accountType'] == "2":
		del dict['username']
		del dict['userEmail']
	elif dict['accountType'] == "3":
		del dict['username']
		del dict['mobile']

# 1代表用户名为主,2代表手机号码为主,3代表邮箱为主
REGISTER_ACCOUNT_TYPE = (
	('1','1--用户名'),
	('2','2--手机号码'),
	('3','3--邮箱'),
)

def api_function(dict):
	if dict['loginType'] == "1":
		del dict['QQ']
		del dict['Email']
		del dict['MSN']
		del dict['weixin']
		del dict['sinaweibo']
		del dict['KLD']
	elif dict['loginType'] == "2":
		del dict['QQ']
		del dict['mobile']
		del dict['MSN']
		del dict['weixin']
		del dict['sinaweibo']
		del dict['KLD']
	elif dict['loginType'] == "3":
		del dict['Email']
		del dict['mobile']
		del dict['MSN']
		del dict['weixin']
		del dict['sinaweibo']
		del dict['KLD']
	elif dict['loginType'] == "4":
		del dict['Email']
		del dict['mobile']
		del dict['QQ']
		del dict['weixin']
		del dict['sinaweibo']
		del dict['KLD']
	elif dict['loginType'] == "5":
		del dict['Email']
		del dict['mobile']
		del dict['QQ']
		del dict['MSN']
		del dict['sinaweibo']
		del dict['KLD']
	elif dict['loginType'] == "6":
		del dict['Email']
		del dict['mobile']
		del dict['QQ']
		del dict['weixin']
		del dict['MSN']
		del dict['KLD']
	elif dict['loginType'] == "7":
		del dict['Email']
		del dict['mobile']
		del dict['QQ']
		del dict['weixin']
		del dict['sinaweibo']
		del dict['MSN']

#1手机号码登录；2用户邮箱登陆；3QQ登录；4MSN登录；5微信登陆；6新浪微博;7第三方信任账户
LOGIN_TYPE = (
	('1','1--手机号码登录'),
	('2','2--邮箱登陆'),
	('3','3--QQ登录'),
	('4','4--MSN登录'),
	('5','5--微信登陆'),
	('6','6--新浪微博'),
	('7','7--第三方信任账户'),
)

# def api_function(dict):
# 	if dict['gender'] == "1":
# 		del dict['Female']
# 		del dict['Neutral']
# 	elif dict['gender'] == "2":
# 		del dict['man']
# 		del dict['Neutral']
# 	elif dict['gender'] == "3":
# 		del dict['man']
# 		del dict['Female']

# 1男,2女,3中性
GENDER_TYPE = (
	('1','1--男'),
	('2','2--女'),
	('3','3--中性'),
)

# def api_function(dict):
# 	if dict['numberType'] == "0":
# 		del dict['talk_key']
# 		del dict['Sound_record']
# 	elif dict['numberType'] == "1":
# 		del dict['number']
# 		del dict['Sound_record']
# 	elif dict['numberType'] == "4":
# 		del dict['number']
# 		del dict['talk_key']

# 0表示两个号码,1代表吐槽键,4代表录音键
NUMBER_TYPE = (
	('0','0--两个号码'),
	('1','1--吐槽键'),
	('4','4--录音键'),
)


# def api_function(dict):
# 	if dict['numberType'] == "0":
# 		del dict['one']
# 		del dict['four']
# 	elif dict['numberType'] == "1":
# 		del dict['all']
# 		del dict['four']
# 	elif dict['numberType'] == "4":
# 		del dict['all']
# 		del dict['one']

#0表示两个号码都恢复默认值；1表示一号键callcenter恢复默认值；4，表示四号键sos恢复默认
NUMBER_TYPE = (
	('0','0--两个号码都恢复默认值'),
	('1','1--一号键callcenter恢复默认值'),
	('4','4--四号键sos恢复默认'),
)


#创建道客帐户
class classAddCustomAccount(forms.Form):
	username = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  ) 
	mobile = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	userEmail = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	daokePassword = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	accountType = forms.ChoiceField( choices = REGISTER_ACCOUNT_TYPE , widget=forms.Select(attrs={'class':'form-control' } ))
	nickname = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def addCustomAccount(req):
	api_uri = "accountapi/v2/addCustomAccount"
	return templateApp(req, classAddCustomAccount, api_uri , sys._getframe().f_code.co_name, before_sign = add_custom_before_sign)

#IMEI预入库
class classApiPrestroge(forms.Form):
	IMEI = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def apiPrestroge(req):
	api_uri = "accountapi/v2/apiPrestroge"
	return templateApp(req, classApiPrestroge, api_uri , sys._getframe().f_code.co_name)

#绑定第三方账户与语镜账号
class classAssociateAccountWithAccountID(forms.Form):
	#accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" ) 
	account = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	loginType = forms.ChoiceField( choices = LOGIN_TYPE ,widget = forms.Select(attrs = {'class':'form-control' } ))
	accessToken = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def associateAccountWithAccountID(req):
	api_uri = "accountapi/v2/associateAccountWithAccountID"
	return templateApp(req, classAssociateAccountWithAccountID, api_uri , sys._getframe().f_code.co_name)

#判断IMEI是否允许绑定
class classCheckImei(forms.Form):
	IMEI = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def checkImei(req):
	api_uri = "accountapi/v2/checkImei"
	return templateApp(req, classCheckImei, api_uri , sys._getframe().f_code.co_name)

#检查用户是否绑定IMEI
class classCheckIsBindImei(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" ) 
	accessToken = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def checkIsBindImei(req):
	api_uri = "accountapi/v2/checkIsBindImei"
	return templateApp(req, classCheckIsBindImei, api_uri , sys._getframe().f_code.co_name)

#用户登陆
class classCheckLogin(forms.Form):
	# accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" ) 
	username = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	daokePassword = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	clientIP = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' , 'value':"127.0.0.1" } )) 
def checkLogin(req):
	api_uri = "accountapi/v2/checkLogin"
	return templateApp(req, classCheckLogin, api_uri , sys._getframe().f_code.co_name)

#判断是否允许注册
class classCheckRegistration(forms.Form):
	username = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def checkRegistration(req):
	api_uri = "accountapi/v2/checkRegistration"
	return templateApp(req, classCheckRegistration, api_uri , sys._getframe().f_code.co_name)

#解绑imei
class classDisconnectAccount(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" ) 
	accessToken = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def disconnectAccount(req):
	api_uri = "accountapi/v2/disconnectAccount"
	return templateApp(req, classDisconnectAccount, api_uri , sys._getframe().f_code.co_name)

#更新用户资料
class classFixUserInfo(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" ) 
	nickname = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	mobile = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	userEmail = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	gender = forms.ChoiceField( choices = GENDER_TYPE , widget = forms.Select(attrs = {'class':'form-control' } ))
	accessToken = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def fixUserInfo(req):
	api_uri = "accountapi/v2/fixUserInfo"
	return templateApp(req, classFixUserInfo, api_uri , sys._getframe().f_code.co_name)

#添加第三方帐户
class classGenerateDaokeAccount(forms.Form):
	account = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	loginType = forms.ChoiceField( choices = LOGIN_TYPE ,widget = forms.Select(attrs = {'class':'form-control' } ))
	nickname = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def generateDaokeAccount(req):
	api_uri = "accountapi/v2/generateDaokeAccount"
	return templateApp(req, classGenerateDaokeAccount, api_uri , sys._getframe().f_code.co_name)

#通过第三方帐户得到账户编号
class classGetAccountIDByAccount(forms.Form):
	account = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	loginType = forms.ChoiceField( choices = LOGIN_TYPE ,widget = forms.Select(attrs = {'class':'form-control' } ))
	clientIP = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' , 'value':"127.0.0.1" } ))

def getAccountIDByAccount(req):
	api_uri = "accountapi/v2/getAccountIDByAccount"
	return templateApp(req, classGetAccountIDByAccount, api_uri , sys._getframe().f_code.co_name)

#通过手机号码得到帐户编号
class classGetAccountIDFromMobile(forms.Form):
	mobile = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def getAccountIDFromMobile(req):
	api_uri = "accountapi/v2/getAccountIDFromMobile"
	return templateApp(req, classGetAccountIDFromMobile, api_uri , sys._getframe().f_code.co_name)

#获取用户自定义参数
class classGetCustomArgs(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" ) 
	accessToken = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def getCustomArgs(req):
	api_uri = "accountapi/v2/getCustomArgs"
	return templateApp(req, classGetCustomArgs, api_uri , sys._getframe().f_code.co_name)

#得到IMEI和手机号
class classGetImeiPhone(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" ) 
	accessToken = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def getImeiPhone(req):
	api_uri = "accountapi/v2/getImeiPhone"
	return templateApp(req, classGetImeiPhone, api_uri , sys._getframe().f_code.co_name)

#得到终端信息
class classGetMirrtalkInfoByImei(forms.Form):
	IMEI = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def getMirrtalkInfoByImei(req):
	api_uri = "accountapi/v2/getMirrtalkInfoByImei"
	return templateApp(req, classGetMirrtalkInfoByImei, api_uri , sys._getframe().f_code.co_name)

#得到手机验证码
class classGetMobileVerificationCode(forms.Form):
	mobile = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	# content = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def getMobileVerificationCode(req):
	api_uri = "accountapi/v2/getMobileVerificationCode"
	return templateApp(req, classGetMobileVerificationCode, api_uri , sys._getframe().f_code.co_name)

#得到用户自定义号码
class classGetUserCustomNumber(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" ) 
	numberType = forms.ChoiceField( choices = NUMBER_TYPE ,widget = forms.Select(attrs = {'class':'form-control' } ))
	accessToken = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def getUserCustomNumber(req):
	api_uri = "accountapi/v2/getUserCustomNumber"
	return templateApp(req, classGetUserCustomNumber, api_uri , sys._getframe().f_code.co_name)

#得到用户资料
class classGetUserInfo(forms.Form):
	username = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def getUserInfo(req):
	api_uri = "accountapi/v2/getUserInfo"
	return templateApp(req, classGetUserInfo, api_uri , sys._getframe().f_code.co_name)

#获取用户信息
class classGetUserInformation(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label= "accountID" )
	accessToken = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def getUserInformation(req):
	api_uri = "accountapi/v2/getUserInformation"
	return templateApp(req, classGetUserInformation, api_uri , sys._getframe().f_code.co_name)

#判断帐户是否在线
class classJudgeOnlineAccounJ(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" ) 
	accessToken = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def judgeOnlineAccount(req):
	api_uri = "accountapi/v2/judgeOnlineAccount"
	return templateApp(req, classJudgeOnlineAccounJ, api_uri , sys._getframe().f_code.co_name)

#判断给定手机号是否在线
class classJudgeOnlineMobile(forms.Form):
	mobile = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def judgeOnlineMobile(req):
	api_uri = "accountapi/v2/judgeOnlineMobile"
	return templateApp(req, classJudgeOnlineMobile, api_uri , sys._getframe().f_code.co_name)

#重置用户自定义号码
class classResetUserCustomNumber(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" )
	numberType = forms.ChoiceField( choices = NUMBER_TYPE ,widget = forms.Select(attrs = {'class':'form-control' } ))
	accessToken = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } )) 

def resetUserCustomNumber(req):
	api_uri = "accountapi/v2/resetUserCustomNumber"
	return templateApp(req, classResetUserCustomNumber, api_uri , sys._getframe().f_code.co_name)

#重置用户道客密码
class classResetUserPassword(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" ) 
	accessToken = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def resetUserPassword(req):
	api_uri = "accountapi/v2/resetUserPassword"
	return templateApp(req, classResetUserPassword, api_uri , sys._getframe().f_code.co_name)

#发送验证URL到邮箱
class classSendVerificationURL(forms.Form):
	userEmail = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	URL = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' ,'value':"https://github.com/jayzh1010"} ))
	content = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' ,'value':"hellonihao" } ))

def sendVerificationURL(req):
	api_uri = "accountapi/v2/sendVerificationURL"
	return templateApp(req, classSendVerificationURL, api_uri , sys._getframe().f_code.co_name)

#设置用户自定义号码
class classSetUserCustomNumber(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" ) 
	call1Number = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	call2Number = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	accessToken = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def setUserCustomNumber(req):
	api_uri = "accountapi/v2/setUserCustomNumber"
	return templateApp(req, classSetUserCustomNumber, api_uri , sys._getframe().f_code.co_name)

#更改用户自定义参数
class classUpdateCustomArgs(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" )
	model = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	customArgs = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	accessToken = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } )) 

def updateCustomArgs(req):
	api_uri = "accountapi/v2/updateCustomArgs"
	return templateApp(req, classUpdateCustomArgs, api_uri , sys._getframe().f_code.co_name)

#更改用户道客密码
class classUpdateUserPassword(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" ) 
	oldPassword = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	newPassword = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	accessToken = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def updateUserPassword(req):
	api_uri = "accountapi/v2/updateUserPassword"
	return templateApp(req, classUpdateUserPassword, api_uri , sys._getframe().f_code.co_name)

#绑定imei
class classUserBindAccountMirrtalk(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" ) 
	IMEI = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	accessToken = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def userBindAccountMirrtalk(req):
	api_uri = "accountapi/v2/userBindAccountMirrtalk"
	return templateApp(req, classUserBindAccountMirrtalk, api_uri , sys._getframe().f_code.co_name)

#验证手机或邮箱
class classVerifyEmailOrMobile(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" )
	email = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	mobile = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	accessToken = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } )) 

def verifyEmailOrMobile(req):
	api_uri = "accountapi/v2/verifyEmailOrMobile"
	return templateApp(req, classVerifyEmailOrMobile, api_uri , sys._getframe().f_code.co_name)

#车机设备号与道客imei关联
class classAssociateDeviceIDWithImei(forms.Form):
	deviceID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	model = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def associateDeviceIDWithImei(req):
	api_uri = "accountapi/v2/associateDeviceIDWithImei"
	return templateApp(req, classAssociateDeviceIDWithImei, api_uri , sys._getframe().f_code.co_name)

#获取用户昵称
class classGetUserData(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" ) 
	field = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	accessToken = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def getUserData(req):
	api_uri = "accountapi/v2/getUserData"
	return templateApp(req, classGetUserData, api_uri , sys._getframe().f_code.co_name)

# 获取手机号对应的验证码
class classGetDynamicVerifycode(forms.Form):
	mobile = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def getDynamicVerifycode(req):
	api_uri = "accountapi/v2/getDynamicVerifycode"
	return templateApp(req, classGetDynamicVerifycode, api_uri , sys._getframe().f_code.co_name)

# 认证新生成的验证码
class classCheckDynamicVerifycode(forms.Form):
	mobile = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	verifyCode = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
def checkDynamicVerifycode(req):
	api_uri = "accountapi/v2/checkDynamicVerifycode"
	return templateApp(req, classCheckDynamicVerifycode, api_uri , sys._getframe().f_code.co_name)

#手机用户获取密码重置的验证码
class classGetPassWordVerifyCode(forms.Form):
	mobile = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def getPassWordVerifyCode(req):
	api_uri = "accountapi/v2/getPassWordVerifyCode"
	return templateApp(req, classGetPassWordVerifyCode, api_uri , sys._getframe().f_code.co_name)

#手机用户根据验证码重置新密码
class classResetPassWordWithMobileVerifyCode(forms.Form):
	mobile = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	verifyCode = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	newPassword = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def resetPassWordWithMobileVerifyCode(req):
	api_uri = "accountapi/v2/resetPassWordWithMobileVerifyCode"
	return templateApp(req, classResetPassWordWithMobileVerifyCode, api_uri , sys._getframe().f_code.co_name)	
#=====================================道客账户 end======================================================





#=====================================oauth begin======================================================
#开发者相关API
#第三方开发者注册身份信息
class classRegisterIdentityInfo(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" )
	developerType = forms.ChoiceField( choices = DEVELOPER_TYPE, widget = forms.Select(attrs={'class':'form-control'}))
	developerName = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	province = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	city = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	address = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	postcode = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	email = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	phone = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	website = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	emergencyContactName = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	emergencyContactPhone = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	IDCardPictureURL = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	businessLicensePictureURL = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	taxRegistrationPictureURL = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	organizationCodePictureURL = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def registerIdentityInfo(req):
	api_uri = "oauth/v2/registerIdentityInfo"
	return templateApp(req, classRegisterIdentityInfo, api_uri , sys._getframe().f_code.co_name)

#合并到registerIdentityInfo
# class classDeveloperIdAdd(forms.Form):
# 	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" )
# 	developerType = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
# 	IDCardPicture = forms.ImageField()  
# 	businessLicensePicture = forms.ImageField()  
# 	taxRegistrationPicture = forms.ImageField()  
# 	organizationCodePicture = forms.ImageField()

# def developerIdAdd(req):
# 	api_uri = "oauth/v2/developerIdAdd"
# 	return templateApp(req, classDeveloperIdAdd, api_uri , sys._getframe().f_code.co_name)

#管理后台审核开发者状态
class classManageDeveloperStatus(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" )
	developerType = forms.ChoiceField( choices = DEVELOPER_TYPE, widget = forms.Select(attrs={'class':'form-control'}))
	status = forms.ChoiceField( choices = DEVELOPER_STATUS, widget = forms.Select(attrs={'class':'form-control'}))

def manageDeveloperStatus(req):
	api_uri = "oauth/v2/manageDeveloperStatus"
	return templateApp(req, classManageDeveloperStatus, api_uri , sys._getframe().f_code.co_name)

#获取开发者资料
class classGetDeveloperInfo(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" )

def getDeveloperInfo(req):
	api_uri = "oauth/v2/getDeveloperInfo"
	return templateApp(req, classGetDeveloperInfo, api_uri , sys._getframe().f_code.co_name)

#更新开发者资料
class classUpdateIdentityInfo(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" )
	province = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	city = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	address = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	postcode = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	email = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	phone = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	website = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	emergencyContactName = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	emergencyContactPhone = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def updateIdentityInfo(req):
	api_uri = "oauth/v2/updateIdentityInfo"
	return templateApp(req, classUpdateIdentityInfo, api_uri , sys._getframe().f_code.co_name)

#管理后台获取开发者信息
class classManageDeveloperInfo(forms.Form):
	status = forms.ChoiceField( choices = GET_DEVELOPER_TYPE, widget = forms.Select(attrs={'class':'form-control'}))
	startPage = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control',  'value':"1" } ))
	pageCount = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control',  'value':"20" } ))
	startTime = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	endTime = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def manageDeveloperInfo(req):
	api_uri = "oauth/v2/manageDeveloperInfo"
	return templateApp(req, classManageDeveloperInfo, api_uri , sys._getframe().f_code.co_name)

#第三方开发者应用管理
#获取appKey信息
class classGetAppKeyInfo(forms.Form):
	clientAppKey = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def getAppKeyInfo(req):
	api_uri = "oauth/v2/getAppKeyInfo"
	return templateApp(req, classGetAppKeyInfo, api_uri , sys._getframe().f_code.co_name)

#生成新应用
class classCreateNewApp(forms.Form):
	developerType = forms.ChoiceField( choices = OAUTH_DEVELOPER_TYPE, widget = forms.Select(attrs={'class':'form-control'}))
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" ) 
	name = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	website = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	appLogo = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	remark = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def createNewApp(req):
	api_uri = "oauth/v2/createNewApp"
	return templateApp(req, classCreateNewApp, api_uri , sys._getframe().f_code.co_name)

#审核第三方应用状态
class classManageAppStatus(forms.Form):
	clientAppKey = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	status = forms.ChoiceField( choices = THIRD_PARTY_APP_STATUS, widget = forms.Select(attrs={'class':'form-control'}))
	reasonRejection = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def manageAppStatus(req):
	api_uri = "oauth/v2/manageAppStatus"
	return templateApp(req, classManageAppStatus, api_uri , sys._getframe().f_code.co_name)


#获取开发者的应用信息，输入参数为appKey,sign,accountID,validity
class classGetDeveloperAppInfo(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" ) 
	validity = forms.ChoiceField( choices = VALIDITY_TYPE, widget = forms.Select(attrs={'class':'form-control'}))

def getDeveloperAppInfo(req):
	api_uri = "oauth/v2/getDeveloperAppInfo"
	return templateApp(req, classGetDeveloperAppInfo, api_uri , sys._getframe().f_code.co_name)

#开发者申请提升应用等级appKey,sign,accountID,clientAppKey,appliedLevel
# class classApplyRaiseAppLevel(forms.Form):
# 	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" ) 
# 	clientAppKey = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
# 	appliedLevel = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

# def applyRaiseAppLevel(req):
# 	api_uri = "oauth/v2/applyRaiseAppLevel"
# 	return templateApp(req, classApplyRaiseAppLevel, api_uri , sys._getframe().f_code.co_name)

# #管理后台获取所有应用等级变更信息appKey,sign,status,startPage,pageCount,startTime,endTime.
# class classManageAppLevelChangeInfo(forms.Form):
# 	status = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
# 	startPage = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
# 	pageCount = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
# 	startTime = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
# 	endTime = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

# def manageAppLevelChangeInfo(req):
# 	api_uri = "oauth/v2/manageAppLevelChangeInfo"
# 	return templateApp(req, classManageAppLevelChangeInfo, api_uri , sys._getframe().f_code.co_name)

# #管理后台更改应用等级appKey,sign,clientAppKey,level
# class classManageAppChangeLevel(forms.Form):
# 	clientAppKey = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
# 	level = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

# def manageAppChangeLevel(req):
# 	api_uri = "oauth/v2/manageAppChangeLevel"
# 	return templateApp(req, classManageAppChangeLevel, api_uri , sys._getframe().f_code.co_name)

#设置OAUTH授权频次控制
class classSetAppFreqInfo(forms.Form):
	clientAppKey = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	apiName = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	frequencyType = forms.ChoiceField( choices = OAUTH_FREQUENCY_TYPE, widget = forms.Select(attrs={'class':'form-control'}))
	customType = forms.ChoiceField( choices = OAUTH_CUSTOM_TYPE, widget = forms.Select(attrs={'class':'form-control'}))
	requestCount = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	#暂时不支持
	# startTime = forms.ChoiceField( choices = OAUTH_NOT_SUPPORT_NOW, widget = forms.Select(attrs={'class':'form-control'}))
	# endTime = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	remark = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def setAppFreqInfo(req):
	api_uri = "oauth/v2/setAppFreqInfo"
	return templateApp(req, classSetAppFreqInfo, api_uri , sys._getframe().f_code.co_name)	

#获取OAUTH授权频次控制
class classGetAppFreqInfo(forms.Form):
	clientAppKey = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	apiName = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def getAppFreqInfo(req):
	api_uri = "oauth/v2/getAppFreqInfo"
	return templateApp(req, classGetAppFreqInfo, api_uri , sys._getframe().f_code.co_name)

#更新OAUTH授权频次控制
class classUpdateAppFreqInfo(forms.Form):
	clientAppKey = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	apiName = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	frequencyType = forms.ChoiceField( choices = OAUTH_FREQUENCY_TYPE, widget = forms.Select(attrs={'class':'form-control'}))
	customType = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	requestCount = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	# startTime = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	# endTime = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	remark = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def updateAppFreqInfo(req):
	api_uri = "oauth/v2/updateAppFreqInfo"
	return templateApp(req, classUpdateAppFreqInfo, api_uri , sys._getframe().f_code.co_name)		

#授权认证
# class classGetAuthCode(forms.Form):
# 	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" )
# 	clientAppKey = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
# 	redirectURL = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
# 	scope = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

# def getAuthCode(req):
# 	api_uri = "oauth/v2/getAuthCode"
# 	return templateApp(req, classGetAuthCode, api_uri , sys._getframe().f_code.co_name)

# class classGetAccessToken(forms.Form):
# 	code = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" ) 
# 	redirectURL = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
# 	grantType = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

# def getAccessToken(req):
# 	api_uri = "oauth/v2/getAccessToken"
# 	return templateApp(req, classGetAccessToken, api_uri , sys._getframe().f_code.co_name)

# class classRefreshAccessToken(forms.Form):
# 	refreshToken =  forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
# 	redirectURL = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
# 	grantType = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

# def refreshAccessToken(req):
# 	api_uri = "oauth/v2/refreshAccessToken"
# 	return templateApp(req, classRefreshAccessToken, api_uri , sys._getframe().f_code.co_name)

class classGetPasswordToken(forms.Form):
	username = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	daokePassword = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	redirectURL = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	scope = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	grantType = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def getPasswordToken(req):
	api_uri = "oauth/v2/getPasswordToken"
	return templateApp(req, classGetPasswordToken, api_uri , sys._getframe().f_code.co_name)

class classGetImplicitToken(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" )
	clientAppKey = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	redirectURL = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	scope = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	grantType = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def getImplicitToken(req):
	api_uri = "oauth/v2/getImplicitToken"
	return templateApp(req, classGetImplicitToken, api_uri , sys._getframe().f_code.co_name)

#trust
class classGetTrustAuthCode(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" )
	scope = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control','value':"userInfo,realTimeInfo,collectInfo,drivingInfo,weibo,reward,bindmirrtalk" } ))

def getTrustAuthCode(req):
	api_uri = "oauth/v2/getTrustAuthCode"
	return templateApp(req, classGetTrustAuthCode, api_uri , sys._getframe().f_code.co_name)

class classGetTrustAccessCode(forms.Form):
	code = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	grantType = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control','value':'authorizationCode' } ))
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" )
	scope = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control','value':"userInfo,realTimeInfo,collectInfo,drivingInfo,weibo,reward,bindmirrtalk"  } ))

def getTrustAccessCode(req):
	api_uri = "oauth/v2/getTrustAccessCode"
	return templateApp(req, classGetTrustAccessCode, api_uri , sys._getframe().f_code.co_name)

class classRefreshTrustAccessToken(forms.Form):
	refreshToken = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	grantType = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def refreshTrustAccessToken(req):
	api_uri = "oauth/v2/refreshTrustAccessToken"
	return templateApp(req, classRefreshTrustAccessToken, api_uri , sys._getframe().f_code.co_name)

class classGetScopeInfo(forms.Form):
	startPage = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control',  'value':"1" } ))
	pageCount = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control',  'value':"20" } ))

def getScopeInfo(req):
	api_uri = "oauth/v2/getScopeInfo"
	return templateApp(req, classGetScopeInfo, api_uri , sys._getframe().f_code.co_name)
#=====================================oauth end======================================================

#=====================================clientcustom begin======================================================

class classSetCustomInfo(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" )
	actionType = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	customType = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	customParameter = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	accessToken = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def setCustomInfo(req):
	api_uri = "clientcustom/v2/setCustomInfo"
	return templateApp(req, classSetCustomInfo, api_uri , sys._getframe().f_code.co_name )

class classSetSubscribeMsg(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" )
	subParameter = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def setSubscribeMsg(req):
	api_uri = "clientcustom/v2/setSubscribeMsg"
	return templateApp(req, classSetSubscribeMsg, api_uri , sys._getframe().f_code.co_name )

# <<<<<<< HEAD
# class classApplyMicroChannel(forms.Form):
# 	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" )
# 	channelName = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
# 	channelIntroduction = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
# 	channelCityCode = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
# 	channelCatalogID = forms.ChoiceField( choices = CATALOG_LIST, widget = forms.Select(attrs={'class':'form-control'} ) )
# 	channelCatalogUrl = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
# 	openType = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
# 	isVerity = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
# 	channelKeyWords = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

# def applyMicroChannel(req):
# 	api_uri = "clientcustom/v2/applyMicroChannel"
# 	return templateApp(req, classApplyMicroChannel, api_uri , sys._getframe().f_code.co_name )

# class classCheckApplyMicroChannel(forms.Form):
# 	checkAccountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" )
# 	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ) , label = "accountID")
# 	channelNumber = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
# 	checkRemark = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
# 	checkStatus = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
# 	channelRemark = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
# 	channelRemark = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

# def checkApplyMicroChannel(req):
# 	api_uri = "clientcustom/v2/checkApplyMicroChannel"
# 	return templateApp(req, classCheckApplyMicroChannel, api_uri , sys._getframe().f_code.co_name )

# class classFetchMicroChannel(forms.Form):
# 	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ) , label = "accountID")
# 	channelNumber = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
# 	checkStatus = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
# 	infoType = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
# 	startPage = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
# 	pageCount = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
# 	cityCode = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
# 	channelName = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
# 	catalogID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
# 	channelKeyWords = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))


# def fetchMicroChannel(req):
# 	api_uri = "clientcustom/v2/fetchMicroChannel"
# 	return templateApp(req, classFetchMicroChannel, api_uri , sys._getframe().f_code.co_name )

# class classFollowMicroChannel(forms.Form):
# 	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ) , label = "accountID")
# 	uniqueCode = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
# 	followType = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
# 	channelNumber = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))


# def followMicroChannel(req):
# 	api_uri = "clientcustom/v2/followMicroChannel"
# 	return templateApp(req, classFollowMicroChannel, api_uri , sys._getframe().f_code.co_name )
# =======
# >>>>>>> 000bceea47371730bdc901ac40276e59f84d636f

class classResetInviteUniqueCode(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ) , label = "accountID")
	channelNumber = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	channelType = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def resetInviteUniqueCode(req):
	api_uri = "clientcustom/v2/resetInviteUniqueCode"
	return templateApp(req, classResetInviteUniqueCode, api_uri , sys._getframe().f_code.co_name )


#=====================================clientcustom end======================================================




#=====================================reward begin======================================================

class classAddDepositInfo(forms.Form):
	IMEI = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  ) 
	depositPassword = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control','value':"123456"})  ) 

def addDepositInfo(req):
	api_uri = "rewardapi/v2/addDepositInfo"
	return templateApp(req, classAddDepositInfo, api_uri , sys._getframe().f_code.co_name )

class classUserFinanceConsume(forms.Form):
	expenseAccountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	incomeAccountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	daokePassword = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	MEPoints = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	WEPoints = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	businessID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	tradeNumber = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	withdrawAccount = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	changedType = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	remark = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	endTime = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	callbackURL = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )

def userFinanceConsume(req):
	api_uri = "rewardapi/v2/userFinanceConsume"
	return templateApp(req, classUserFinanceConsume, api_uri , sys._getframe().f_code.co_name )

class classBusinessRegisterInfo(forms.Form):
	username = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	mobile = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	businessName = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	returnType = forms.ChoiceField( choices = REWARD_RETURN_TYPE, widget = forms.Select(attrs={'class':'form-control'} ) )
	parentID = forms.ChoiceField( choices = REWARD_PARENT_ID, widget = forms.Select(attrs={'class':'form-control'} ) )
	isChannel = forms.ChoiceField( choices = REWARD_IS_CHANNEL, widget = forms.Select(attrs={'class':'form-control'} ) )
	receiverName = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	receiverPhone = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	receiverAddress = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	allowExchange = forms.ChoiceField( choices = REWARD_ALLOW_EXCHANGE, widget = forms.Select(attrs={'class':'form-control'} ) )
	bonusType = forms.ChoiceField( choices = REWARD_BONUS_TYPE, widget = forms.Select(attrs={'class':'form-control'} ) )
	shareInfo = forms.ChoiceField( choices = REWARD_SHARE_INFO, widget = forms.Select(attrs={'class':'form-control'} ) )
	bonusReturnTarget = forms.ChoiceField( choices = REWARD_BONUS_RETURN_TARGET_TYPE, widget = forms.Select(attrs={'class':'form-control'} ) )
	userBonusMax = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	businessBonusMax = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	bonusReturnMonth = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	remark = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )

def businessRegisterInfo(req):
	api_uri = "rewardapi/v2/businessRegisterInfo"
	return templateApp(req, classBusinessRegisterInfo, api_uri , sys._getframe().f_code.co_name )


#=====
class classDonateDaoke(forms.Form):
	donatorAccountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	donatorName = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	daokePassword = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	isAnonymous = forms.ChoiceField( choices = REWARD_IS_ANONYMOUS, widget = forms.Select(attrs={'class':'form-control'} ) )
	amount = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	donatedType = forms.ChoiceField( choices = REWARD_DONATED_TYPE, widget = forms.Select(attrs={'class':'form-control'} ) )
	regularDonation = forms.ChoiceField( choices = REWARD_REGULAR_DONATION, widget = forms.Select(attrs={'class':'form-control'} ) )

def donateDaoke(req):
	api_uri = "rewardapi/v2/donateDaoke"
	return templateApp(req, classDonateDaoke , api_uri, sys._getframe().f_code.co_name)

class classFetchDonationInfo(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ) , label = "accountID")
	startTime = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	endTime = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	startPage =	forms.CharField( widget=forms.TextInput(attrs={'class':'form-control',  'value':"1" })  )
	pageCount =	forms.CharField( widget=forms.TextInput(attrs={'class':'form-control',  'value':"20" })  )


def fetchDonationInfo(req):
	api_uri = "rewardapi/v2/fetchDonationInfo"
	return templateApp(req, classFetchDonationInfo , api_uri, sys._getframe().f_code.co_name)

class classGetAllRankInfo(forms.Form):
	time = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	type = forms.ChoiceField( choices = REWARD_TYPE, widget = forms.Select(attrs={'class':'form-control'} ) )
	startRank = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	endRank = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	startPage = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control',  'value':"1"})  )
	pageCount = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control',  'value':"20"})  )

def getAllRankInfo(req):
	api_uri = "rewardapi/v2/getAllRankInfo"
	return templateApp(req, classGetAllRankInfo , api_uri, sys._getframe().f_code.co_name)

class classGetRewardRank(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ) , label = "accountID")
	time = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	type = forms.ChoiceField( choices = REWARD_TYPE, widget = forms.Select(attrs={'class':'form-control'} ) )

def getRewardRank(req):
	api_uri = "rewardapi/v2/getRewardRank"
	return templateApp(req, classGetRewardRank , api_uri, sys._getframe().f_code.co_name)

class classGetAllWithdrawInfo(forms.Form):
	withdrawType = forms.ChoiceField( choices = REWARD_WITHDRAW_TYPE, widget = forms.Select(attrs={'class':'form-control'} ) )

def getAllWithdrawInfo(req):
	api_uri = "rewardapi/v2/getAllWithdrawInfo"
	return templateApp(req, classGetAllWithdrawInfo , api_uri, sys._getframe().f_code.co_name)

class classTransferEnterpriseAccount(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ) , label = "accountID")
	businessID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	receiptID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	withdrawAmount = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	remark = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )

def transferEnterpriseAccount(req):
	api_uri = "rewardapi/v2/transferEnterpriseAccount"
	return templateApp(req, classTransferEnterpriseAccount , api_uri, sys._getframe().f_code.co_name)

class classTransferOwnAccount(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ) , label = "accountID")
	receiptID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	withdrawAmount = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	withdrawAccount = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	withdrawAccountType = forms.ChoiceField( choices = REWARD_WITHDRAW_ACCOUNT_TYPE, widget = forms.Select(attrs={'class':'form-control'} ) )
	remark = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )

def transferOwnAccount(req):
	api_uri = "rewardapi/v2/transferOwnAccount"
	return templateApp(req, classTransferOwnAccount , api_uri, sys._getframe().f_code.co_name)

class classGetBalanceDetail(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ) , label = "accountID")
	startTime = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	endTime = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	startPage = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control',  'value':"1"})  )
	pageCount = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control',  'value':"20"})  )
	moneyType = forms.ChoiceField( choices = REWARD_WITHDRAW_ACCOUNT_TYPE, widget = forms.Select(attrs={'class':'form-control'} ) )

def getBalanceDetail(req):
	api_uri = "rewardapi/v2/getBalanceDetail"
	return templateApp(req, classGetBalanceDetail , api_uri, sys._getframe().f_code.co_name)

class classFetchDepositHistory(forms.Form):
	IMEI = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	startTime = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	endTime = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	startPage = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control',  'value':"1"})  )
	pageCount = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control',  'value':"20"})  )
	showType = forms.ChoiceField( choices = REWARD_WITHDRAW_ACCOUNT_TYPE, widget = forms.Select(attrs={'class':'form-control'} ) )
	isAll = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	moneyType = forms.ChoiceField( choices = REWARD_WITHDRAW_ACCOUNT_TYPE, widget = forms.Select(attrs={'class':'form-control'} ) )

def fetchDepositHistory(req):
	api_uri = "rewardapi/v2/fetchDepositHistory"
	return templateApp(req, classFetchDepositHistory , api_uri, sys._getframe().f_code.co_name)

class classGetUserDepositInfo(forms.Form):
	IMEI = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	showType = forms.ChoiceField( choices = REWARD_WITHDRAW_ACCOUNT_TYPE, widget = forms.Select(attrs={'class':'form-control'} ) )
	moneyType = forms.ChoiceField( choices = REWARD_WITHDRAW_ACCOUNT_TYPE, widget = forms.Select(attrs={'class':'form-control'} ) )

def getUserDepositInfo(req):
	api_uri = "rewardapi/v2/getUserDepositInfo"
	return templateApp(req, classGetUserDepositInfo , api_uri, sys._getframe().f_code.co_name)

class classGetRewardAmountByMileage(forms.Form):
	IMEI = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ) , label = "accountID")
	mileage = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	moneyType = forms.ChoiceField( choices = REWARD_WITHDRAW_ACCOUNT_TYPE, widget = forms.Select(attrs={'class':'form-control'} ) )

def getRewardAmountByMileage(req):
	api_uri = "rewardapi/v2/getRewardAmountByMileage"
	return templateApp(req, classGetRewardAmountByMileage , api_uri, sys._getframe().f_code.co_name)

class classCrashRecharge(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ) , label = "accountID")
	changedAmount = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	remark = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	businessID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	endTime = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	moneyType = forms.ChoiceField( choices = REWARD_WITHDRAW_ACCOUNT_TYPE, widget = forms.Select(attrs={'class':'form-control'} ) )

def crashRecharge(req):
	api_uri = "rewardapi/v2/crashRecharge"
	return templateApp(req, classCrashRecharge , api_uri, sys._getframe().f_code.co_name)

class classApplyWithdrawDeposit(forms.Form):
	IMEI = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ) , label = "accountID")
	depositPassword = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	applyWithdrawAmount = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	autoWithdraw = forms.ChoiceField( choices = REWARD_IS_ANONYMOUS, widget = forms.Select(attrs={'class':'form-control'} ) )
	moneyType = forms.ChoiceField( choices = REWARD_WITHDRAW_ACCOUNT_TYPE, widget = forms.Select(attrs={'class':'form-control'} ) )

def applyWithdrawDeposit(req):
	api_uri = "rewardapi/v2/applyWithdrawDeposit"
	return templateApp(req, classApplyWithdrawDeposit , api_uri, sys._getframe().f_code.co_name)

class classApplyWithdrawMoney(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ) , label = "accountID")
	daokePassword = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	applyWithdrawAmount = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	withdrawAccount = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	withdrawAccountType = forms.ChoiceField( choices = REWARD_WITHDRAW_ACCOUNT_TYPE, widget = forms.Select(attrs={'class':'form-control'} ) )
	callbackURL = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	tradeNumber = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	moneyType = forms.ChoiceField( choices = REWARD_WITHDRAW_ACCOUNT_TYPE, widget = forms.Select(attrs={'class':'form-control'} ) )

def applyWithdrawMoney(req):
	api_uri = "rewardapi/v2/applyWithdrawMoney"
	return templateApp(req, classApplyWithdrawMoney , api_uri, sys._getframe().f_code.co_name)

class classGetUserFinanceInfo(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ) , label = "accountID")
	moneyType = forms.ChoiceField( choices = REWARD_WITHDRAW_ACCOUNT_TYPE, widget = forms.Select(attrs={'class':'form-control'} ) )

def getUserFinanceInfo(req):
	api_uri = "rewardapi/v2/getUserFinanceInfo"
	return templateApp(req, classGetUserFinanceInfo , api_uri, sys._getframe().f_code.co_name)

class classTransferOwnAccount(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ) , label = "accountID")
	receiptID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	withdrawAmount = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	withdrawAccount = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	withdrawAccountType = forms.ChoiceField( choices = REWARD_WITHDRAW_ACCOUNT_TYPE, widget = forms.Select(attrs={'class':'form-control'} ) )
	remark = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )

def transferOwnAccount(req):
	api_uri = "rewardapi/v2/transferOwnAccount"
	return templateApp(req, classTransferOwnAccount , api_uri, sys._getframe().f_code.co_name)


class classConfirmCancelContract(forms.Form):
	IMEI = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )

def confirmCancelContract(req):
	api_uri = "rewardapi/v2/confirmCancelContract"
	return templateApp(req, classConfirmCancelContract , api_uri, sys._getframe().f_code.co_name)

class classConfirmExchangeGoods(forms.Form):
	oldIMEI = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	newIMEI = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )

def confirmExchangeGoods(req):
	api_uri = "rewardapi/v2/confirmExchangeGoods"
	return templateApp(req, classConfirmExchangeGoods , api_uri, sys._getframe().f_code.co_name)


#=====================================reward end======================================================


#====================================weme setting begin================================
# 判断用户是否在线
class classCheckIsOnline(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" )

def checkIsOnline(req):
	api_uri = "clientcustom/v3/checkIsOnline"
	return templateApp(req, classCheckIsOnline, api_uri , sys._getframe().f_code.co_name ,api_html = "apiform_ex.html"  )


#==================================
# 获取用户按键 2015-05-22 
class classGetUserkeyInfo(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" )
	actionType = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) )

def getUserkeyInfo(req):
	api_uri = "clientcustom/v2/getUserkeyInfo"
	return templateApp(req, classGetUserkeyInfo, api_uri , sys._getframe().f_code.co_name )

# 设置用户按键 2015-05-22

class classSetUserkeyInfo(forms.Form):
	tmp_parameter = '''{"count":"3",
"list": [{	"actionType":"3","customType":"10",
			"customParameter":""
		},
		{	"actionType":"4","customType":"10",
			"customParameter":"000000153"
		},
		{	"actionType":"5","customType":"10",
			"customParameter":"000000153"
		}]
}'''

	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" )
	# initial  初始化值 
	parameter = forms.CharField(initial= tmp_parameter , widget=forms.Textarea(attrs={'class':'form-control','cols':800} ) )

def setUserkeyInfo(req):
	api_uri = "clientcustom/v2/setUserkeyInfo"
	return templateApp(req, classSetUserkeyInfo, api_uri , sys._getframe().f_code.co_name )

#====================================weme setting end


#---------------------------map api ===begin===================================================================

class classUpdatePOIAttr(forms.Form):
	ID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) )
	NM = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) )
	ST = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) )
	TP = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) )
	BD = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) )
	LD = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) )
	DP = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) )
	TT = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) )

def updatePOIAttr(req):
	api_uri = "mapapi/v2/updatePOIAttr"
	return templateApp(req, classUpdatePOIAttr, api_uri , sys._getframe().f_code.co_name )
#---------------------------map api ====end====================================================================


#------------------------------------ main debug add  api  ========begin===========================
class classUserConfigInfo(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	model = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )

def userConfigInfo(req):
	api_uri = "accountapi/v2/getCustomArgs"
	return templateApp(req, classUserConfigInfo, api_uri , sys._getframe().f_code.co_name )


class classSetAppKeySecret(forms.Form):
	appKey = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	secret = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )

def setAppKeySecret(req):
	api_uri = ""
	return templateApp_Debug(req, classSetAppKeySecret, api_uri  , sys._getframe().f_code.co_name )

class classDevicePowerOn(forms.Form):
	imei = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	imsi = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	mod = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )

def devicePowerOn(req):
	api_uri = "config"
	return templateApp(req, classDevicePowerOn, api_uri  , sys._getframe().f_code.co_name )	
#------------------------------------ main debug add  api  ========end===========================


#------------------------------------ dfs  api  ========end===========================


class classTxtToVoice(forms.Form):
	text = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )

def txtToVoice(req):
	api_uri = "dfsapi/v2/txt2voice"
	return templateApp(req, classTxtToVoice, api_uri , sys._getframe().f_code.co_name )

#------------------------------------ dfs  api  ========end===========================



#------------------------------------ web  api  ========end===========================
class classSendSms(forms.Form):
	mobile = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) )
	content= forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' ,'value':"短信测试信息"}) )
	platform = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) )
	is_times = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) )
def sendSms(req):
	api_uri = "webapi/v2/sendSms"
	return templateApp(req, classSendSms, api_uri , sys._getframe().f_code.co_name )
#------------------------------------ web  api  ========end===========================



#---------------------------------------serverChannel ---begin

class classGetCustomDefineInfo(forms.Form):
	defineName = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) )
	actionType = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) )
	startPage = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control','value':"1"}) )
	pageCount = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control','value':"20"}) )

def getCustomDefineInfo(req):
	api_uri = "clientcustom/v2/getCustomDefineInfo"
	return templateApp(req, classGetCustomDefineInfo, api_uri , sys._getframe().f_code.co_name )
#---------------------------------------serverChannel ---begin


class classTTSDemo(forms.Form):
	text = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'} ) )
	
def TTSDemo(req):
	api_uri = "dfsapi/v2/txt2voice"
	return templateApp(req, classTTSDemo, api_uri , sys._getframe().f_code.co_name)
