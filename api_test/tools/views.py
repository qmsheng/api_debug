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

appKey = '4223273916'
secret = 'DA00D00CBFECD61E4EA4FA830FCEEA4C96C5683D'
# appKey = "184269830"
# secret = "931E498698AB2D9B1D93F419E572D2ACCA981488"
# apiHost = "115.231.73.17"
# apiHost = "192.168.1.27"
# apiHost = "192.168.184.136"

# 点6
# appKey = "2064302565"
# secret = "BB9318B102E320C09B8AB9D5229B5668DB1C00D0"

#沙箱
# accountID = "SsYYnzgsdw"
# appKey = "1111111111"
# secret = "34F9CD6587D98875D2D4FA393C42ADE63298230F"

# apiHost = "127.0.0.1"
apiHost = "192.168.1.207"
# apiHost = "192.168.11.135"
# apiHost = "115.231.73.17"
# apiHost = "192.168.184.129"

apiPort = "80"




def my_urlencode(str) :
    reprStr = repr(str).replace(r'\x', '%')
    return reprStr[1:-1]

def http_post_api(url, data ,api_host , api_port ):
	tmp_api_host = ""
	tmp_api_port = 0

	if api_host != None and api_port != None :
		
		tmp_api_host = api_host
		tmp_api_port = api_port
	else:
		tmp_api_host = apiHost
		tmp_api_port = apiPort

	print("http_post_api===enter111")
	print(tmp_api_host)
	print(tmp_api_port)

	# requrl = "http://" + tmp_api_host + ":" + tmp_api_port +  "/" + url
	requrl = "http://{0}:{1}/{2}".format( tmp_api_host , tmp_api_port , url )

	print("http_post_api===enter222" + requrl)

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


def get_sign(dict):
	dict['appKey'] = appKey
	dict['secret'] = secret
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

		dict['sign'] = get_sign(dict)

		if after_sign != None:
			after_sign(dict)

		request_msg = dict_to_str(dict)

		result_msg = ""
		object_data = None

		try:
			result_msg = http_post_api(uri,request_msg, api_host, api_port )
			object_data = json.loads(result_msg)
		except :
			print result_msg
			pass

		return render_to_response(api_html, {'form':form, "api_action": api_action ,  "api_account": req.session['username'] , "uri": uri,  "request_msg":request_msg, "result_msg":result_msg, "object_data":object_data } )
	else:
		form = template_form()
		return render_to_response(api_html,{'form':form, "api_action": api_action , "api_account": req.session['username'] })



#=======================================login begin=========================================================================

class UserForm(forms.Form):
	username = forms.CharField()


def login(req):
	if req.method == 'POST':
		username = req.POST['username']
		if username and len(username) == 10:
			req.session['username'] = username
			return HttpResponseRedirect("index", { 'username' : username } ) 
		else:
			return render_to_response('login.html', { 'error_msg' : "accountID不正确" }  )
	else:
		uf = UserForm()
		return render_to_response('login.html',{'uf':uf})

def logout(req):
	username = req.session.get('username')
	if username:
		del req.session['username']
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
		return render_to_response('top.html', { 'username' : req.session['username'] } )
	else:
		return HttpResponseRedirect("login") 

def index(req):
	username = req.session.get('username')
	if username:
		return render_to_response('index.html', { 'username' : username } )
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
CATALOG_LIST = (
	('','所有以2开头为主播频道3是群聊频道'),
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
	('300008' ,'300008--旅行'),
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
	('1','1--公司管理频道(status  2 关闭频道)'),
	('2','2--管理员管理频道(status 1 正常 2 禁言用户 3 拉黑用户)')
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

class classApplySecretChannel(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' }) , label = "accountID" ) 
	channelName = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	channelIntroduction = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	channelCityCode = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})   )
	channelCatalogID = forms.ChoiceField( choices = CATALOG_LIST, widget = forms.Select(attrs={'class':'form-control'} ) )
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
	channelOpenType = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	channelIntro = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})   )
	channelCatalogID = forms.ChoiceField( choices = CATALOG_LIST, widget = forms.Select(attrs={'class':'form-control'} ) )
	channelLogoUrl = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	channelCitycode = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})   )
	channelKeyWords = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )

def modifySecretChannelInfo(req):
	api_uri = "clientcustom/v2/modifySecretChannelInfo"
	return templateApp(req, classModifySecretChannelInfo, api_uri , sys._getframe().f_code.co_name)




class classManageSecretChannel(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' }) , label = "accountID" ) 
	channelNumber = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	infoType = forms.ChoiceField(choices=MANAGE_SECRET_TYPE  , widget = forms.Select(attrs={'class':'form-control'}   ) )
	userAccountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' }) , label = "accountID" ) 
	curStatus = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
def manageSecretChannel(req):
	api_uri = "clientcustom/v2/manageSecretChannelUsers"
	return templateApp(req, classManageSecretChannel, api_uri , sys._getframe().f_code.co_name)


class classSetCustomInfo(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' }) , label = "accountID" ) 
	actionType = forms.ChoiceField( choices = SECRET_USERKEY,  widget=forms.Select(attrs={'class':'form-control'} ) )
	customType = forms.ChoiceField( choices = SECRET_CUSTOMTYPE, widget=forms.Select(attrs={'class':'form-control' })  ) 
	customParameter = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' })  ) 
def setCustomInfo(req):
	api_uri = "clientcustom/v2/setCustomInfo"
	return templateApp(req, classSetCustomInfo, api_uri , sys._getframe().f_code.co_name)





class classFetchSecretChannel(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" ) 
	channelName = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'} ) )
	channelNumber = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'} ))
	cityCode = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'} ))
	status = forms.ChoiceField(choices=JOIN_CHANNEL_STATUS  , widget = forms.Select(attrs={'class':'form-control'}   ) )
	catalogID = forms.ChoiceField( choices = CATALOG_LIST, widget = forms.Select(attrs={'class':'form-control'} ) )
	infoType = forms.ChoiceField(choices=FETCH_SECRET_INFO_TYPE  , widget = forms.Select(attrs={'class':'form-control'}   ) )
	startPage = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' , 'value':"1" } ))
	pageCount = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' , 'value':"20" } ))


def fetchSecretChannel(req):
	api_uri = "clientcustom/v2/fetchSecretChannel"
	return templateApp(req, classFetchSecretChannel, api_uri , sys._getframe().f_code.co_name)


class classSecretMessage(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" ) 
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


class classTTSDemo(forms.Form):
	text = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'} ) )
	
def TTSDemo(req):
	api_uri = "dfsapi/v2/txt2voice"
	return templateApp(req, classTTSDemo, api_uri , sys._getframe().f_code.co_name)


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
	startPage = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	pageCount = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

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
	channelCatalogID = forms.ChoiceField( choices = CATALOG_LIST, widget = forms.Select(attrs={'class':'form-control'} ) )
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

class classCheckApplyMicroChannel(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' }) , label = "accountID" )
	checkAccountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' }) ) 
	channelNumber = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	checkRemark = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	checkStatus = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	channelRemark = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})   )
	applyIdx = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})   )

def checkApplyMicroChannel(req):
	api_uri = "clientcustom/v2/checkApplyMicroChannel"
	return templateApp(req, classCheckApplyMicroChannel, api_uri , sys._getframe().f_code.co_name)


class classFetchMicroChannel(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' }) , label = "accountID" )
	channelStatus = forms.ChoiceField( choices = MICROCHANNEL_STATUS, widget = forms.Select(attrs={'class':'form-control'} ) )
	cityCode = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	catalogID = forms.ChoiceField( choices = CATALOG_LIST, widget = forms.Select(attrs={'class':'form-control'} ) )
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
	channelCatalogID = forms.ChoiceField( choices = CATALOG_LIST, widget = forms.Select(attrs={'class':'form-control'} ) )
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
	api_uri = "clientcustom/v2/followMicroChannel  "
	return templateApp(req, classFollowMicroChannel, api_uri , sys._getframe().f_code.co_name)


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


def api_function(dict):
	if dict['gender'] == "1":
		del dict['Female']
		del dict['Neutral']
	elif dict['gender'] == "2":
		del dict['man']
		del dict['Neutral']
	elif dict['gender'] == "3":
		del dict['man']
		del dict['Female']

# 1男,2女,3中性
GENDER_TYPE = (
	('1','1--男'),
	('2','2--女'),
	('3','3--中性'),
)

def api_function(dict):
	if dict['numberType'] == "0":
		del dict['talk_key']
		del dict['Sound_record']
	elif dict['numberType'] == "1":
		del dict['number']
		del dict['Sound_record']
	elif dict['numberType'] == "4":
		del dict['number']
		del dict['talk_key']

# 0表示两个号码,1代表吐槽键,4代表录音键
NUMBER_TYPE = (
	('0','0--两个号码'),
	('1','1--吐槽键'),
	('4','4--录音键'),
)


def api_function(dict):
	if dict['numberType'] == "0":
		del dict['one']
		del dict['four']
	elif dict['numberType'] == "1":
		del dict['all']
		del dict['four']
	elif dict['numberType'] == "4":
		del dict['all']
		del dict['one']

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
	accessToken = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	nickname = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	mobile = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	userEmail = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	gender = forms.ChoiceField( choices = GENDER_TYPE , widget = forms.Select(attrs = {'class':'form-control' } ))

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
	accessToken = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	numberType = forms.ChoiceField( choices = NUMBER_TYPE ,widget = forms.Select(attrs = {'class':'form-control' } ))

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
	accessToken = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } )) 
	numberType = forms.ChoiceField( choices = NUMBER_TYPE ,widget = forms.Select(attrs = {'class':'form-control' } ))

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
	accessToken = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	call1Number = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	call2Number = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def setUserCustomNumber(req):
	api_uri = "accountapi/v2/setUserCustomNumber"
	return templateApp(req, classSetUserCustomNumber, api_uri , sys._getframe().f_code.co_name)

#更改用户自定义参数
class classUpdateCustomArgs(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" )
	accessToken = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } )) 
	model = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	customArgs = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def updateCustomArgs(req):
	api_uri = "accountapi/v2/updateCustomArgs"
	return templateApp(req, classUpdateCustomArgs, api_uri , sys._getframe().f_code.co_name)

#更改用户道客密码
class classUpdateUserPassword(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" ) 
	accessToken = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	oldPassword = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	newPassword = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def updateUserPassword(req):
	api_uri = "accountapi/v2/updateUserPassword"
	return templateApp(req, classUpdateUserPassword, api_uri , sys._getframe().f_code.co_name)

#绑定imei
class classUserBindAccountMirrtalk(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" ) 
	accessToken = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	IMEI = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def userBindAccountMirrtalk(req):
	api_uri = "accountapi/v2/userBindAccountMirrtalk"
	return templateApp(req, classUserBindAccountMirrtalk, api_uri , sys._getframe().f_code.co_name)

#验证手机或邮箱
class classVerifyEmailOrMobile(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" )
	accessToken = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } )) 
	email = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	mobile = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

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
	accessToken = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	field = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
def getUserData(req):
	api_uri = "accountapi/v2/getUserData"
	return templateApp(req, classGetUserData, api_uri , sys._getframe().f_code.co_name)

# 获取手机号对应的验证码
class classGetOauthVerifycode(forms.Form):
	mobile = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def getOauthVerifycode(req):
	api_uri = "accountapi/v2/getOauthVerifycode"
	return templateApp(req, classGetOauthVerifycode, api_uri , sys._getframe().f_code.co_name)

# 认证新生成的验证码
class classCheckOauthVerifycode(forms.Form):
	mobile = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	verifyCode = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
def checkOauthVerifycode(req):
	api_uri = "accountapi/v2/checkOauthVerifycode"
	return templateApp(req, classCheckOauthVerifycode, api_uri , sys._getframe().f_code.co_name)


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
	startPage = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	pageCount = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
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
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" ) 
	website = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	name = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	appLogo = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

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

#OAUTH授权频次控制
class classSetAppFreqInfo(forms.Form):
	clientAppKey = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	apiName = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	requestCount = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	frequencyType = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	remark = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def setAppFreqInfo(req):
	api_uri = "oauth/v2/setAppFreqInfo"
	return templateApp(req, classSetAppFreqInfo, api_uri , sys._getframe().f_code.co_name)	

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
	scope = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def getTrustAuthCode(req):
	api_uri = "oauth/v2/getTrustAuthCode"
	return templateApp(req, classGetTrustAuthCode, api_uri , sys._getframe().f_code.co_name)

class classGetTrustAccessCode(forms.Form):
	code = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	grantType = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" )
	scope = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def getTrustAccessCode(req):
	api_uri = "oauth/v2/getTrustAccessCode"
	return templateApp(req, classGetTrustAccessCode, api_uri , sys._getframe().f_code.co_name)

class classRefreshTrustAccessToken(forms.Form):
	refreshToken = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	grantType = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def refreshTrustAccessToken(req):
	api_uri = "oauth/v2/refreshTrustAccessToken"
	return templateApp(req, classRefreshTrustAccessToken, api_uri , sys._getframe().f_code.co_name)
#=====================================oauth end======================================================

#=====================================reward begin======================================================

class classAddDepositInfo(forms.Form):
	IMEI = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  ) 
	depositPassword = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control','value':"123456"})  ) 

def addDepositInfo(req):
	api_uri = "rewardapi/v2/addDepositInfo"
	return templateApp(req, classAddDepositInfo, api_uri , sys._getframe().f_code.co_name )

#=====================================reward end======================================================


#====================================weme setting begin================================
# 判断用户是否在线
class classCheckIsOnline(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" )

def checkIsOnline(req):
	api_uri = "clientcustom/v3/checkIsOnline"
	return templateApp(req, classCheckIsOnline, api_uri , sys._getframe().f_code.co_name)
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