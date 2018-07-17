# -*- coding: utf-8 -*-
import syslog
import pyotp

OTP_SECRET = "YOU OTP SECRET KEY"
WHITE_IP = ["YOU BYPASS IP"]
def  otp_auth(code):
        totp = pyotp.TOTP(OTP_SECRET)
        if totp.now() == code:
                return True
        else:
                return False

def otp_log(msg):
    syslog.openlog(facility=syslog.LOG_AUTH)
    syslog.syslog("otp auth log: "+msg)
    syslog.closelog()

def otp_code():
	totp = pyotp.TOTP(OTP_SECRET)
	return totp.now()

def pam_sm_authenticate(pamh, flags, argv):
	for white in WHITE_IP:
		if pamh.rhost == white:
			otp_log("white ip login,ip is "+pamh.rhost)
			return pamh.PAM_SUCCESS
        resp = pamh.conversation(pamh.Message(pamh.PAM_PROMPT_ECHO_OFF,'Password:'))
        code = resp.resp[-6:]
        if otp_auth(code):
                pamh.authtok = resp.resp[:-6]
                otp_log("login success,code is "+resp.resp[-6:])
        else:
                pamh.authtok = ""
                otp_log("login fail,code is "+resp.resp[-6:])
		otp_log("login fail,code must is "+otp_code())
        return pamh.PAM_SUCCESS

def pam_sm_setcred(pamh, flags, argv):

       return pamh.PAM_SUCCESS

