# -*- coding: utf-8 -*-
import pyotp
import os
secret = pyotp.random_base32()
with open('auth.py','r') as f:
      lines = f.readlines()
      lines[4] = 'OTP_SECRET = "%s"\n'%(secret)
with open('auth.py','w') as f:
      f.writelines(lines)
url = pyotp.totp.TOTP(secret).provisioning_uri("test@test.com", issuer_name="jxotp")
cmd = 'echo "%s" | qrencode -o - -t UTF8'%(url)
print("请使用微信小程序 运维密码 扫描二维码")
print("友情提醒，如果需要设置白名单IP，可通过修改/lib64/security/auth.py文件进行设置")
print("详情请查看github文档说明")
#print cmd
os.system(cmd)

