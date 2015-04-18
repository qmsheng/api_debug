#!/usr/bin/python
#-*- coding: UTF-8 -*-

#from django.conf.urls.defaults import *
from django.conf.urls import patterns, url, include
from django.http import HttpResponse
from tools.views import *

import sys

reload = reload(sys) 
sys.setdefaultencoding('gb18030')


# from django.conf import settings
# if settings.DEBUG is False:
# url(r'^static/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.STATIC_ROOT } ),


urlpatterns = patterns (
			'',
			url(r'^$',login),
			url(r'^login$',login),
			url(r'^logout$',logout),
			url(r'^index$', index),
			url(r'^left$', left),
			url(r'^right$',right),
			url(r'^top$',top),

			#------------user secret channel  begin-------------------------
			url(r'^applySecretChannel$',applySecretChannel),
			url(r'^fetchSecretChannel$',fetchSecretChannel),
			url(r'^secretChannelMessage$',secretChannelMessage),
			url(r'^joinSecretChannel$',joinSecretChannel),
			url(r'^quitSecretChannel$',quitSecretChannel),
			url(r'^veritySecretChannelMessage$',veritySecretChannelMessage),
			url(r'^getSecretChannelInfo$',getSecretChannelInfo),
			url(r'^getUserJoinListSecretChannel$',getUserJoinListSecretChannel),
			#------------user secret channel  end-------------------------

			
			#--------------道客账户 begin-------------------------
		
			url(r'^addCustomAccount$',addCustomAccount),
			url(r'^apiPrestroge$',apiPrestroge),
			url(r'^associateAccountWithAccountID$',associateAccountWithAccountID),
			url(r'^checkImei$',checkImei),
			url(r'^checkIsBindImei$',checkIsBindImei),
			url(r'^checkLogin$',checkLogin),
			url(r'^checkRegistration$',checkRegistration),
			url(r'^disconnectAccount$',disconnectAccount),
			url(r'^fixUserInfo$',fixUserInfo),
			url(r'^generateDaokeAccount$',generateDaokeAccount),
			url(r'^getAccountIDByAccount$',getAccountIDByAccount),
			url(r'^getAccountIDFromMobile$',getAccountIDFromMobile),
			url(r'^getCustomArgs$',getCustomArgs),
			url(r'^getImeiPhone$',getImeiPhone),
			url(r'^getMirrtalkInfoByImei$',getMirrtalkInfoByImei),
			url(r'^getMobileVerificationCode$',getMobileVerificationCode),
			url(r'^getUserCustomNumber$',getUserCustomNumber),
			url(r'^getUserInfo$',getUserInfo),
			url(r'^getUserInformation$',getUserInformation),
			url(r'^judgeOnlineAccount$',judgeOnlineAccount),
			url(r'^judgeOnlineMobile$',judgeOnlineMobile),
			url(r'^resetUserCustomNumber$',resetUserCustomNumber),
			url(r'^resetUserPassword$',resetUserPassword),
			url(r'^sendVerificationURL$',sendVerificationURL),
			url(r'^setUserCustomNumber$',setUserCustomNumber),
			url(r'^updateCustomArgs$',updateCustomArgs),
			url(r'^updateUserPassword$',updateUserPassword),
			url(r'^userBindAccountMirrtalk$',userBindAccountMirrtalk),
			url(r'^verifyEmailOrMobile$',verifyEmailOrMobile),
			url(r'^associateDeviceIDWithImei$',associateDeviceIDWithImei),

			#--------------道客账户 end-------------------------

			#--------------daoke oauth---------------
			# url(r'^getScopeInfo$',getScopeInfo),
			# url(r'^getTrustAuthCode$',getTrustAuthCode),
			# url(r'^getTrustAccessCode$',getTrustAccessCode),
			# url(r'^refreshTrustAccessToken$',refreshTrustAccessToken),
			#developer
			url(r'^registerIdentityInfo$',registerIdentityInfo),
			url(r'^developerIdAdd$',developerIdAdd),
			url(r'^manageDeveloperStatus$',manageDeveloperStatus),
			url(r'^getDeveloperInfo$',getDeveloperInfo),
			url(r'^updateIdentityInfo$',updateIdentityInfo),
			url(r'^manageDeveloperInfo$',manageDeveloperInfo),

			#developer's app
			url(r'^getAppKeyInfo$',getAppKeyInfo),
			url(r'^createNewApp$',createNewApp),
			url(r'^getDeveloperAppInfo$',getDeveloperAppInfo),
			url(r'^applyRaiseAppLevel$',applyRaiseAppLevel),
			url(r'^manageAppLevelChangeInfo$',manageAppLevelChangeInfo),
			url(r'^manageAppChangeLevel$',manageAppChangeLevel),
			url(r'^setAppFreqInfo$',setAppFreqInfo),

			#authrization
			url(r'^getAuthCode$',getAuthCode),
			url(r'^getAccessToken$',getAccessToken),
			url(r'^refreshAccessToken$',refreshAccessToken),
			url(r'^getImplicitToken$',getImplicitToken),
			url(r'^getPasswordToken$',getPasswordToken),

			#oauth for KLD
			url(r'^getTrustAuthCode$',getTrustAuthCode),
			url(r'^getTrustAccessCode$',getTrustAccessCode),
			url(r'^refreshTrustAccessToken$',refreshTrustAccessToken),

			#--------------daoke oauth---------------


			#------------reward api begin-----------------------
			url(r'^addDepositInfo$',addDepositInfo),
			#------------reward api end-----------------------


	)