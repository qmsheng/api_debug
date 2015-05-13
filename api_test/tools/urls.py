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
			url(r'^getCatalogInfo$',getCatalogInfo),
			url(r'^applySecretChannel$',applySecretChannel),
			url(r'^fetchSecretChannel$',fetchSecretChannel),
			url(r'^secretChannelMessage$',secretChannelMessage),
			url(r'^joinSecretChannel$',joinSecretChannel),
			url(r'^quitSecretChannel$',quitSecretChannel),
			url(r'^veritySecretChannelMessage$',veritySecretChannelMessage),
			url(r'^getSecretChannelInfo$',getSecretChannelInfo),
			url(r'^getUserJoinListSecretChannel$',getUserJoinListSecretChannel),
			url(r'^manageSecretChannel$',manageSecretChannel),
			url(r'^setCustomInfo$',setCustomInfo),
			url(r'^modifySecretChannelInfo$',modifySecretChannelInfo),
			url(r'^getCustomInfo$',getCustomInfo),

			#------------user secret channel  end-------------------------
			url(r'^getCatalogInfo$',getCatalogInfo  ),

			#------------user microChannel begin----------------------------
			url(r'^modifyMicroChannel$',modifyMicroChannel ),
			url(r'^followMicroChannel$',followMicroChannel ),
			url(r'^applyMicroChannel$',applyMicroChannel ),
			url(r'^checkApplyMicroChannel$',checkApplyMicroChannel ),
			url(r'^fetchMicroChannel$',fetchMicroChannel ),
			url(r'^getMicroChannelInfo$',getMicroChannelInfo ),
			url(r'^getBossFollowListMicroChannel$',getBossFollowListMicroChannel ),

			# url(r'^getBossFollowListMicroChannel$',getBossFollowListMicroChannel ),
			# url(r'^resetInviteUniqueCode$',resetInviteUniqueCode ),

			#------------user microChannel end------------------------------

			
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
			url(r'^getUserData$',getUserData),
			# url(r'^getOauthVerifycode$',getOauthVerifycode),
			# url(r'^checkOauthVerifycode$',checkOauthVerifycode),
			url(r'^getDynamicVerifycode$',getDynamicVerifycode),
			url(r'^checkDynamicVerifycode$',checkDynamicVerifycode),


			#--------------道客账户 end-------------------------

			#--------------daoke oauth---------------
			# url(r'^getScopeInfo$',getScopeInfo),
			# url(r'^getTrustAuthCode$',getTrustAuthCode),
			# url(r'^getTrustAccessCode$',getTrustAccessCode),
			# url(r'^refreshTrustAccessToken$',refreshTrustAccessToken),
			#developer
			url(r'^registerIdentityInfo$',registerIdentityInfo),
			# url(r'^developerIdAdd$',developerIdAdd),
			url(r'^manageDeveloperStatus$',manageDeveloperStatus),
			url(r'^getDeveloperInfo$',getDeveloperInfo),
			url(r'^updateIdentityInfo$',updateIdentityInfo),
			url(r'^manageDeveloperInfo$',manageDeveloperInfo),

			#developer's app
			url(r'^getAppKeyInfo$',getAppKeyInfo),
			url(r'^createNewApp$',createNewApp),
			url(r'^getDeveloperAppInfo$',getDeveloperAppInfo),
			# url(r'^applyRaiseAppLevel$',applyRaiseAppLevel),
			# url(r'^manageAppLevelChangeInfo$',manageAppLevelChangeInfo),
			# url(r'^manageAppChangeLevel$',manageAppChangeLevel),
			url(r'^setAppFreqInfo$',setAppFreqInfo),
			url(r'^getAppFreqInfo$',getAppFreqInfo),
			url(r'^updateAppFreqInfo$',updateAppFreqInfo),
			url(r'^manageAppStatus$',manageAppStatus),
			
			#authrization
			# url(r'^getAuthCode$',getAuthCode),
			# url(r'^getAccessToken$',getAccessToken),
			# url(r'^refreshAccessToken$',refreshAccessToken),
			url(r'^getImplicitToken$',getImplicitToken),
			url(r'^getPasswordToken$',getPasswordToken),

			#oauth for Trust 
			url(r'^getScopeInfo$',getScopeInfo),
			url(r'^getTrustAuthCode$',getTrustAuthCode),
			url(r'^getTrustAccessCode$',getTrustAccessCode),
			url(r'^refreshTrustAccessToken$',refreshTrustAccessToken),

			#--------------daoke oauth---------------

			#-------------clientcustom setting begin---------
			url(r'^setCustomInfo$',setCustomInfo),
			url(r'^setSubscribeMsg$',setSubscribeMsg),
			url(r'^applyMicroChannel$',applyMicroChannel),
			url(r'^checkApplyMicroChannel$',checkApplyMicroChannel),
			url(r'^fetchMicroChannel$',fetchMicroChannel),
			url(r'^followMicroChannel$',followMicroChannel),
			url(r'^resetInviteUniqueCode$',resetInviteUniqueCode),
			url(r'^setSubscribeMsg$',setSubscribeMsg),

			#-------------clientcustom setting end-----------

			#-------------WEME setting begin---------
			url(r'^checkIsOnline$',checkIsOnline),
			#-------------WEME setting end-----------

			#------------reward api begin-----------------------
			#--添加押金信息
			url(r'^addDepositInfo$',addDepositInfo),
			url(r'^businessRegisterInfo$',businessRegisterInfo),
			#--用户捐赠
			url(r'^donateDaoke$',donateDaoke),
			url(r'^fetchDonationInfo$',fetchDonationInfo),
			url(r'^getAllRankInfo$',getAllRankInfo),
			url(r'^getRewardRank$',getRewardRank),
			#--财务打款
			url(r'^getAllWithdrawInfo$',getAllWithdrawInfo),
			url(r'^transferEnterpriseAccount$',transferEnterpriseAccount),
			url(r'^transferOwnAccount$',transferOwnAccount),
			#--用户查询资金
			url(r'^getBalanceDetail$',getBalanceDetail),
			url(r'^fetchDepositHistory$',fetchDepositHistory),
			url(r'^getUserDepositInfo$',getUserDepositInfo),
			url(r'^getRewardAmountByMileage$',getRewardAmountByMileage),
			url(r'^crashRecharge$',crashRecharge),
			#--用户消费
			url(r'^applyWithdrawDeposit$',applyWithdrawDeposit),
			url(r'^applyWithdrawMoney$',applyWithdrawMoney),
			url(r'^getUserFinanceInfo$',getUserFinanceInfo),
			url(r'^transferOwnAccount$',transferOwnAccount),
			url(r'^userFinanceConsume$',userFinanceConsume),
			#--设备取消合约
			url(r'^confirmCancelContract$',confirmCancelContract),
			url(r'^confirmExchangeGoods$',confirmExchangeGoods),
			
			#------------reward api end-----------------------


			#---------------map api-------------------------
			url(r'^updatePOIAttr$',updatePOIAttr),
			#------------------------------------------------

			
			#---------------map api-------------------------
			url(r'^setAppKeySecret$',setAppKeySecret),
			url(r'^userConfigInfo$',userConfigInfo),
			url(r'^devicePowerOn$',devicePowerOn),
			
			#------------------------------------------------

	)
