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
			url(r'^checkIsBindIMEI$',checkIsBindIMEI),
			url(r'^checkIMEI$',checkIMEI),
			url(r'^userBindAccountMirrtalk$',userBindAccountMirrtalk),
			url(r'^disconnectAccount$',disconnectAccount),
			#--------------道客账户 end-------------------------

			#--------------daoke oauth---------------
			url(r'^getScopeInfo$',getScopeInfo),
			url(r'^getTrustAuthCode$',getTrustAuthCode),
			url(r'^getTrustAccessCode$',getTrustAccessCode),
			url(r'^refreshTrustAccessToken$',refreshTrustAccessToken),
			#--------------daoke oauth---------------


	)