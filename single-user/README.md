# jxotp
这就是个新的轮子，技术上没有大的创新，只是更好用一些

目前在centos6/7上测试通过，其他系统自测。

安装如下:

1、# git clone https://github.com/jx-sec/jxotp.git

2、# cd jxotp

3、# sh  install_otp.sh

结果如下:

![image](http://image.3001.net/images/20180719/15319897144140.png!small)

拿出你发财的小手，打开微信小程序，搜索 "运维密码" ，打开后 点击 "添加场景" 扫描二维码即可完成OTP的配置

最后是在服务器上启用OTP功能

\# vi /etc/pam.d/sshd 

在最上一行添加   

auth       optional    pam_python.so auth.py

![image](http://image.3001.net/images/20180719/15319897379551.png!small)

保存文件即可生效，无需重启sshd服务

安装配置过程到此结束，下面校验效果

\# tail -F /var/log/messages

新开个窗口登陆服务器，随便输入个密码，如123456

![image](http://image.3001.net/images/20180719/15319897615450.png!small)

日志为”sshd: otp auth log: login user is root,login fail,code is 123456,must 054040″

code is 123456，是取当前输入密码的后六位，即123456

must is 054040, 054040是当前OTP生成的code，需要对比运维密码中的code与服务器的code是否一致，正常服务器时间没问题的话，是一致的

需确保服务器和运维密码的code一致

假设密码为abcdfgww，code为951753，那么当登陆的时候，输入的密码为abcdfgww951753

