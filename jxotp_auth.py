# -*- coding: utf-8 -*-
import syslog
import requests
#SERVER_API_URL = "http://52.163.121.204:8000/otp_auth" 
#OTP_SECRET_KEY = "hellojxotp"
SERVER_API_URL = "http://1.1.1.1:8000/otp_auth"
OTP_SECRET_KEY = "hellojxotp"
import json
def otp_log(msg):
    syslog.openlog(facility=syslog.LOG_AUTH)
    syslog.syslog("otp auth log: "+msg)
    syslog.closelog()

def pam_sm_authenticate(pamh, flags, argv):
	resp = pamh.conversation(pamh.Message(pamh.PAM_PROMPT_ECHO_OFF,'Password:'))
	payload = {'rhost':pamh.rhost,'user':pamh.user,'code':resp.resp[-6:],'otp_secret_key':OTP_SECRET_KEY}
	try:
		req = requests.post(SERVER_API_URL,data=payload,timeout=10)
		http_resp = req.json()
		if http_resp['result'] == 'success':
			pamh.authtok = resp.resp[:-6]
			otp_log("login user is "+pamh.user+",login success,message : "+http_resp['message'])
		elif http_resp['result'] == 'fail':
			pamh.authtok = ""
			otp_log("login user is "+pamh.user+",login fail,message : "+http_resp['message'])
		else:
			otp_log("login user is "+pamh.user+",login error,message : "+http_resp['message'])
		return pamh.PAM_SUCCESS
		
	except:	
		otp_log("otp check error!")
        	return pamh.PAM_SUCCESS

def pam_sm_setcred(pamh, flags, argv):

       return pamh.PAM_SUCCESS

