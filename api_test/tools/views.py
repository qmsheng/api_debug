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

appKey = "184269830"
secret = "931E498698AB2D9B1D93F419E572D2ACCA981488"

# apiHost = "127.0.0.1"
apiHost = "192.168.1.207"
apiPort = "80"

def my_urlencode(str) :
    reprStr = repr(str).replace(r'\x', '%')
    return reprStr[1:-1]

def http_post_api(url, data ,api_host , api_port ):

	tmp_api_host = apiHost
	tmp_api_port = apiPort

	if api_host != None and api_port != None :
		tmp_api_host = api_host
		tmp_api_port = api_port
		
	requrl = "http://" + tmp_api_host + ":" + tmp_api_port +  "/" + url

	try:
		headerdata = {"Host": tmp_api_host }

		conn = httplib.HTTPConnection(tmp_api_host,tmp_api_port)
		conn.request(method="POST",url = requrl,body= data, headers = headerdata) 

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
	print( tmp_str )
	sign = hashlib.sha1(tmp_str).hexdigest().upper()
	print( sign )
	del dict['secret']
	return sign


def templateApp(req, template_form,  uri , api_action , api_html = "apiform.html", api_host = None, api_port = None, api_function = None ):
	if req.method == 'POST':
		form = template_form(req.POST)
		dict = {} 
		for item in req.POST:
			dict[item] = req.POST[item]
		dict['sign'] =get_sign(dict)
		
		if api_function != None:
			api_function(dict)

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
)

#---- 频道类别
CATALOG_SECRET_LIST = (
	('','所有'),
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



class classApplySecretChannel(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' }) , label = "accountID" ) 
	channelName = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	channelIntroduction = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	channelCityCode = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})   )
	channelCatalogID = forms.ChoiceField( choices = CATALOG_SECRET_LIST, widget = forms.Select(attrs={'class':'form-control'} ) )
	channelCatalogUrl = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  )
	openType = forms.ChoiceField( choices = SECRET_OPENTYPE , widget = forms.Select(attrs={'class':'form-control'})  )
	isVerity = forms.ChoiceField( choices = SECRET_VERITY_TYPE ,  widget=forms.Select(attrs={'class':'form-control'})  )


def applySecretChannel(req):
	api_uri = "clientcustom/v2/applySecretChannel"
	return templateApp(req, classApplySecretChannel, api_uri , sys._getframe().f_code.co_name)



class classFetchSecretChannel(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" ) 
	channelName = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'} ) )
	channelNumber = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'} ))
	cityCode = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'} ))
	catalogID = forms.ChoiceField( choices = CATALOG_SECRET_LIST, widget = forms.Select(attrs={'class':'form-control'} ) )
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



class classCreateNewApp(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" ) 
	website = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	name = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def createNewApp(req):
	api_uri = "oauth/v2/createNewApp"
	return templateApp(req, classCreateNewApp, api_uri , sys._getframe().f_code.co_name)











#=====================================道客账户 begin======================================================

def api_function(dict):
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
	('2','1--手机号码'),
	('3','1--邮箱'),
)

class classAddCustomAccount(forms.Form):
	username = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  ) 
	mobile = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	userEmail = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	daokePassword = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))
	accountType = forms.ChoiceField( choices = REGISTER_ACCOUNT_TYPE , widget=forms.Select(attrs={'class':'form-control' } ))
	nickname = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' } ))

def addCustomAccount(req):
	api_uri = "accountapi/v2/addCustomAccount"
	return templateApp(req, classAddCustomAccount, api_uri , sys._getframe().f_code.co_name, )


#是否绑定IMEI
class classCheckIsBindIMEI(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" ) 

def checkIsBindIMEI(req):
	api_uri = "accountapi/v2/checkIsBindImei"
	return templateApp(req, classCheckIsBindIMEI, api_uri , sys._getframe().f_code.co_name)


class classCheckIMEI(forms.Form):
	IMEI = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "IMEI" ) 
		
def checkIMEI(req):
	api_uri = "accountapi/v2/checkImei"
	return templateApp(req, classCheckIMEI, api_uri , sys._getframe().f_code.co_name)

class classUserBindAccountMirrtalk(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" )
	IMEI = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) ) 

def userBindAccountMirrtalk(req):
	api_uri = "accountapi/v2/userBindAccountMirrtalk"
	return templateApp(req, classUserBindAccountMirrtalk, api_uri , sys._getframe().f_code.co_name)

class classDisconnectAccount(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" )

def disconnectAccount(req):
	api_uri = "accountapi/v2/disconnectAccount"
	return templateApp(req, classDisconnectAccount, api_uri , sys._getframe().f_code.co_name)

#=====================================道客账户 end======================================================










#=====================================oauth begin======================================================

class classTestOauth(forms.Form):
	clientAppKey = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  ) 
	redirectURL = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  ) 
	scope = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  ) 

def testOauth(req):
	api_uri = "authorize"
	api_host = "127.0.0.1"
	api_port = "10000"
	return templateApp(req, classTestOauth, api_uri , sys._getframe().f_code.co_name, api_host, api_port  )

class classGetScopeInfo(forms.Form):
	startPage = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' , 'value':"1" } ))
	pageCount = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control' , 'value':"40" } ))

def getScopeInfo(req):
	api_uri = "oauth/v2/getScopeInfo"
	return templateApp(req, classGetScopeInfo, api_uri , sys._getframe().f_code.co_name   )


class classGetTrustAuthCode(forms.Form):
	accountID = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'}) , label = "accountID" )
	scope = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  ) 

def getTrustAuthCode(req):
	api_uri = "oauth/v2/getTrustAuthCode"
	return templateApp(req, classGetTrustAuthCode, api_uri , sys._getframe().f_code.co_name   )


class classGetTrustAccessCode(forms.Form):
	code = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  ) 
	grantType = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control','value':"authorizationCode"})  ) 


def getTrustAccessCode(req):
	api_uri = "oauth/v2/getTrustAccessCode"
	return templateApp(req, classGetTrustAccessCode, api_uri , sys._getframe().f_code.co_name )

class classRefreshTrustAccessToken(forms.Form):
	refreshToken = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control'})  ) 
	grantType = forms.CharField( widget=forms.TextInput(attrs={'class':'form-control','value':"refreshToken"})  ) 

def refreshTrustAccessToken(req):
	api_uri = "oauth/v2/refreshTrustAccessToken"
	return templateApp(req, classRefreshTrustAccessToken, api_uri , sys._getframe().f_code.co_name )


#=====================================oauth end======================================================



