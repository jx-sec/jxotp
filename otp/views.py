# -*- coding:utf-8 –*-
import pyotp
from django.shortcuts import render
from django.http import JsonResponse, Http404, HttpResponse
from django.core import mail
from django.core.mail import send_mail
from email.mime.image import MIMEImage
from otp.models import *
from django.db.models import Q
from datetime import datetime, timedelta, date
import qrcode
import json
from django.utils.six import BytesIO
from django.conf import settings
import sys

reload(sys)
sys.setdefaultencoding('utf8')


def index(request):
    #   username = request.POST['username']
    try:
        request.session['user_id']
        return render(request, 'index.html')
    except:
        return render(request, 'login.html')


# Create your views here.
def auth(code, OTP_SECRET):
    totp = pyotp.TOTP(OTP_SECRET)
    if totp.verify(code, valid_window=2):
        return True
    else:
        return False


def otp_auth(request):
    result = {}
    try:
        client_ip = request.META['REMOTE_ADDR']
        rhost = request.POST['rhost']
        sys_user = request.POST['user']
        code = request.POST['code']
        otp_secret_key = request.POST['otp_secret_key']
        if otp_secret_key == settings.OTP_SECRET_KEY:
            pass
        else:
            otp_log.objects.create(client_ip=request.META['REMOTE_ADDR'], result='error',
                                   message='otp_secret_key error',
                                   time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            result['result'] = "error"
            result['message'] = "The otp_secret_key is error"
            return JsonResponse(result, safe=False)
        config = otp_config.objects.get(user='admin')
        global_check = config.default_global_check
        check_users = config.default_check_user.split(",")
        white_ip = config.default_white_ip.split(",")
        users = otp_user.objects.filter(enable='true')
        try:
            otp_server.objects.get(server_ip=client_ip)
        except:
            if config.default_enable == "true":
                otp_server.objects.create(server_ip=client_ip, enable=config.default_enable)
                otp_log.objects.create(server_ip=client_ip, client_ip=rhost, result='fail',
                                       message='server register', check_user=sys_user,
                                       time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            else:
                result['result'] = "error"
                result['message'] = "The server is not registered"
                return JsonResponse(result, safe=False)
        try:
            server_config = otp_server.objects.get(Q(server_ip=client_ip) & Q(enable='true'))
        except:
            otp_log.objects.create(server_ip=client_ip, client_ip=rhost, result='fail',
                                   message='server is not enable', check_user=sys_user,
                                   time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            result['result'] = "error"
            result['message'] = "The server is not enable"
            return JsonResponse(result, safe=False)

        if config.black_check == 'true':
            now = timezone.now()
            deny_result = otp_alert.objects.filter(client_ip=rhost).filter(server_ip=client_ip).filter(
                time__gte=timezone.now())
            if len(deny_result) == 1:
                otp_log.objects.create(server_ip=client_ip, client_ip=rhost, result='error',
                                       message='The client ip is black', check_user=sys_user,
                                       time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                result['result'] = "error"
                result['message'] = "The client ip is black"
                return JsonResponse(result, safe=False)
            elif len(deny_result) > 1:
                otp_log.objects.create(server_ip=client_ip, client_ip=rhost, result='error',
                                       message='The client ip is black,unknow error', check_user=sys_user,
                                       time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                result['result'] = "error"
                result['message'] = "The client ip is black,unknow error"
                return JsonResponse(result, safe=False)
            check_time = timedelta(minutes=int(config.black_check_time))
            check_result = otp_log.objects.filter(client_ip=rhost).filter(server_ip=client_ip).filter(
                result='fail').filter(
                defalut_time__range=(now - check_time, now)).count()
            if check_result > int(config.black_check_count):
                deny_time = timedelta(minutes=int(config.black_deny_time))
                otp_alert.objects.create(client_ip=rhost, server_ip=client_ip, time=now + deny_time)
                send_emails = []
                send_emails.append(config.black_send_email)
                send_mail(r'jxotp报警，检测到客户端%s对服务器%s进行暴力破解攻击' % (rhost, client_ip),
                          '检测到客户端%s在%s对服务器%s进行暴力破解攻击,在%s分钟内错误次数超过%s次,该IP已被封禁%s分钟' % (
                              rhost, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), client_ip, config.black_check_time,
                              config.black_check_count, config.black_deny_time), 'security@jxwaf.com',
                          send_emails, fail_silently=False)
                otp_log.objects.create(server_ip=client_ip, client_ip=rhost, result='error',
                                       message='The client ip is black init', check_user=sys_user,
                                       time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                result['result'] = "error"
                result['message'] = "The client ip is black init"
                return JsonResponse(result, safe=False)

        if server_config.custom == "true":
            white_ip = server_config.white_ip.split(",")
            global_check = server_config.global_check
            check_users = server_config.check_user.split(",")
            for white in white_ip:
                if rhost == white:
                    result['result'] = "success"
                    result[
                        'message'] = "The client ip in white ip list, system user is " + sys_user + ",client ip is " + rhost + ",server ip is " + client_ip
                    otp_log.objects.create(server_ip=client_ip, client_ip=rhost, result='success',
                                           message='client ip in white ip list', check_user=sys_user,
                                           time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    return JsonResponse(result, safe=False)
            if global_check == 'true':
                for user in users:
                    if auth(code, user.otp_secret):
                        otp_log.objects.create(server_ip=client_ip, client_ip=rhost, result='success',
                                               message='login success', check_user=sys_user,
                                               time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                        result['result'] = "success"
                        result[
                            'message'] = "login success, web user is " + user.user_email + ",system user is " + sys_user + ",client ip is " + rhost + ",server ip is " + client_ip
                        return JsonResponse(result, safe=False)
                    else:

                        otp_log.objects.create(server_ip=client_ip, client_ip=rhost, result='fail',
                                               message='login fail', check_user=sys_user,
                                               time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                        result['result'] = "fail"
                        result[
                            'message'] = "login fail, system user is " + sys_user + ",client ip is " + rhost + ",server ip is " + client_ip
                        return JsonResponse(result, safe=False)
            else:
                users = otp_user.objects.filter(enable='true')
                for check_user in check_users:
                    if check_user == sys_user:
                        for user in users:
                            if auth(code, user.otp_secret):
                                otp_log.objects.create(server_ip=client_ip, client_ip=rhost, result='success',
                                                       message='login success', check_user=sys_user,
                                                       time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                                       user_email=user)
                                result['result'] = "success"
                                result[
                                    'message'] = "login success, web user is " + user.user_email + ",system user is " + sys_user + ",client ip is " + rhost + ",server ip is " + client_ip
                                return JsonResponse(result, safe=False)

                        otp_log.objects.create(server_ip=client_ip, client_ip=rhost, result='fail',
                                               message='login fail', check_user=sys_user,
                                               time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                        result['result'] = "fail"
                        result[
                            'message'] = "system user is " + sys_user + ",client ip is " + rhost + ",server ip is " + client_ip
                        return JsonResponse(result, safe=False)
                    else:
                        otp_log.objects.create(server_ip=client_ip, client_ip=rhost, result='success',
                                               message='login bypass', check_user=sys_user,
                                               time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                        result['result'] = "success"
                        result[
                            'message'] = "login system user is bypass, system user is " + sys_user + ",client ip is " + rhost + ",server ip is " + client_ip
                        return JsonResponse(result, safe=False)
            otp_log.objects.create(server_ip=client_ip, client_ip=rhost, result='error',
                                   message='unkonw error', check_user=sys_user,
                                   time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            result['result'] = "error"
            result[
                'message'] = "login error, unkonw error,system user is " + sys_user + ",client ip is " + rhost + ",server ip is " + client_ip
            return JsonResponse(result, safe=False)

        for white in white_ip:
            if rhost == white:
                result['result'] = "success"
                result[
                    'message'] = "The client ip in white ip list, system user is " + sys_user + ",client ip is " + rhost + ",server ip is " + client_ip
                otp_log.objects.create(server_ip=client_ip, client_ip=rhost, result='success',
                                       message='client ip in white ip list', check_user=sys_user,
                                       time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                return JsonResponse(result, safe=False)
        if global_check == 'true':
            for user in users:
                if auth(code, user.otp_secret):
                    otp_log.objects.create(server_ip=client_ip, client_ip=rhost, result='success',
                                           message='login success', check_user=sys_user,
                                           time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    result['result'] = "success"
                    result[
                        'message'] = "login success, web user is " + user.user_email + ",system user is " + sys_user + ",client ip is " + rhost + ",server ip is " + client_ip
                    return JsonResponse(result, safe=False)
                else:
                    otp_log.objects.create(server_ip=client_ip, client_ip=rhost, result='fail',
                                           message='login fail', check_user=sys_user,
                                           time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    result['result'] = "fail"
                    result[
                        'message'] = "login fail,system user is " + sys_user + ",client ip is " + rhost + ",server ip is " + client_ip
                    return JsonResponse(result, safe=False)
        else:
            users = otp_user.objects.filter(enable='true')
            for check_user in check_users:
                if check_user == sys_user:
                    for user in users:
                        if auth(code, user.otp_secret):
                            otp_log.objects.create(server_ip=client_ip, client_ip=rhost, result='success',
                                                   message='login success', check_user=sys_user,
                                                   time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'), user_email=user)
                            result['result'] = "success"
                            result[
                                'message'] = "login success, web user is " + user.user_email + ",system user is " + sys_user + ",client ip is " + rhost + ",server ip is " + client_ip
                            return JsonResponse(result, safe=False)

                    otp_log.objects.create(server_ip=client_ip, client_ip=rhost, result='fail',
                                           message='login fail', check_user=sys_user,
                                           time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    result['result'] = "fail"
                    result[
                        'message'] = "system user is " + sys_user + ",client ip is " + rhost + ",server ip is " + client_ip
                    return JsonResponse(result, safe=False)
                else:
                    otp_log.objects.create(server_ip=client_ip, client_ip=rhost, result='fail',
                                           message='login fail', check_user=sys_user,
                                           time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    result['result'] = "success"
                    result[
                        'message'] = "login system user is bypass, system user is " + sys_user + ",client ip is " + rhost + ",server ip is " + client_ip
                    return JsonResponse(result, safe=False)
        otp_log.objects.create(server_ip=client_ip, client_ip=rhost, result='error',
                               message='unkonw error', check_user=sys_user,
                               time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        result['result'] = "error"
        result[
            'message'] = "login error, unkonw error,system user is " + sys_user + ",client ip is " + rhost + ",server ip is " + client_ip
        return JsonResponse(result, safe=False)

    except:
        otp_log.objects.create(client_ip=request.META['REMOTE_ADDR'], result='error',
                               message='system error',
                               time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        result['result'] = "error"
        result['message'] = "System Error! REMOTE_ADDR is " + request.META['REMOTE_ADDR']
        return JsonResponse(result, safe=False)


def login(request):
    data = {}
    try:
        json_date = json.loads(request.body)
        user = json_date['user']
        password = json_date['password']
    except:
        data['return_code'] = 0
        return JsonResponse(data, safe=False)

    if user == settings.USERNAME and password == settings.PASSWORD:
        request.session['user_id'] = 'admin'
        try:
            otp_config.objects.get(user='admin')
        except:
            otp_config.objects.create(user='admin')
        data['return_code'] = 2
        return JsonResponse(data, safe=False)
    else:
        data['return_code'] = 4
        return JsonResponse(data, safe=False)


def logout(request):
    try:
        del request.session['user_id']
        return render(request, 'login.html')
    except:
        return render(request, 'login.html')


def server_add(request):
    data = {}
    try:
        user_id = request.session['user_id']
        json_date = json.loads(request.body)
        server_ip = json_date['server_ip']
        enable = json_date['enable']
        global_check = json_date['global_check']
        check_user = json_date['check_user']
        white_ip = json_date['white_ip']
        custom = json_date['custom']
        try:
            otp_server.objects.create(server_ip=server_ip, enable=enable, custom=custom, global_check=global_check,
                                      check_user=check_user, white_ip=white_ip)
        except:
            otp_server.objects.filter(server_ip=server_ip).update(enable=enable, custom=custom,
                                                                  global_check=global_check,
                                                                  check_user=check_user, white_ip=white_ip)
        data['return_code'] = 2
        return JsonResponse(data, safe=False)
    except:
        data['return_code'] = 0
        return JsonResponse(data, safe=False)


def server_del(request):
    data = {}
    try:
        user_id = request.session['user_id']
        json_date = json.loads(request.body)
        server_ip = json_date['server_ip']
        otp_server.objects.get(server_ip=server_ip).delete()
        data['return_code'] = 2
        return JsonResponse(data, safe=False)
    except:
        data['return_code'] = 0
        return JsonResponse(data, safe=False)


def server_list(request):
    data = {}
    try:
        mode = request.GET['mode']
        user_id = request.session['user_id']
        if mode == '0':
            result = otp_server.objects.values('server_ip', 'enable', 'custom', 'global_check', 'check_user',
                                               'white_ip')
            data['return_code'] = 2
            data['result'] = list(result)
            return JsonResponse(data, safe=False)
        elif mode == '1':
            result = otp_server.objects.filter(enable='true').values('server_ip', 'enable', 'custom', 'global_check',
                                                                     'check_user', 'white_ip')
            data['return_code'] = 2
            data['result'] = list(result)
            return JsonResponse(data, safe=False)
        elif mode == '2':
            result = otp_server.objects.filter(enable='false').values('server_ip', 'enable', 'custom', 'global_check',
                                                                      'check_user', 'white_ip')
            data['return_code'] = 2
            data['result'] = list(result)
            return JsonResponse(data, safe=False)
        else:
            data['return_code'] = 1
            data['result'] = 'null'
            return JsonResponse(data, safe=False)
    except:
        data['return_code'] = 0
        return JsonResponse(data, safe=False)


def user_add(request):
    data = {}
    try:
        user_id = request.session['user_id']
        json_date = json.loads(request.body)
        user_email = json_date['user_email']
        otp_secret = json_date['otp_secret']
        enable = json_date['enable']
        try:
            otp_user.objects.create(user_email=user_email, otp_secret=otp_secret,
                                    enable=enable)
        except:
            otp_user.objects.filter(user_email=user_email).update(otp_secret=otp_secret,
                                                                  enable=enable)
        data['return_code'] = 2
        return JsonResponse(data, safe=False)
    except:
        data['return_code'] = 0
        return JsonResponse(data, safe=False)


def user_del(request):
    data = {}
    try:
        user_id = request.session['user_id']
        json_date = json.loads(request.body)
        user_email = json_date['user_email']
        otp_user.objects.get(user_email=user_email).delete()
        data['return_code'] = 2
        return JsonResponse(data, safe=False)
    except:
        data['return_code'] = 0
        return JsonResponse(data, safe=False)


def user_list(request):
    data = {}
    try:
        mode = request.GET['mode']
        user_id = request.session['user_id']
        if mode == '0':
            result = otp_user.objects.values('user_email', 'otp_secret', 'enable')
            data['return_code'] = 2
            # data['result'] = serialize("json", result)
            data['result'] = list(result)
            return JsonResponse(data, safe=False)
        elif mode == '1':
            result = otp_user.objects.filter(enable='true').values('user_email', 'otp_secret', 'enable')
            data['return_code'] = 2
            data['result'] = list(result)
            return JsonResponse(data, safe=False)
        elif mode == '2':
            result = otp_user.objects.filter(enable='false').values('user_email', 'otp_secret', 'enable')
            data['return_code'] = 2
            data['result'] = list(result)
            return JsonResponse(data, safe=False)
        else:
            data['return_code'] = 1
            data['result'] = 'null'
            return JsonResponse(data, safe=False)
    except:
        data['return_code'] = 0
        return JsonResponse(data, safe=False)


def config_list(request):
    data = {}
    try:
        user_id = request.session['user_id']
        result = otp_config.objects.get(user='admin')
        data['return_code'] = 2
        data['result'] = {'default_enable': result.default_enable, "default_global_check": result.default_global_check,
                          "default_white_ip": result.default_white_ip, "default_check_user": result.default_check_user,
                          'black_check_time': result.black_check_time, 'black_check_count': result.black_check_count,
                          'black_send_email': result.black_send_email, 'black_check': result.black_check,
                          'black_deny_time': result.black_deny_time}
        return JsonResponse(data, safe=False)
    except:
        data['return_code'] = 0
        return JsonResponse(data, safe=False)


def config_add(request):
    data = {}
    try:
        user_id = request.session['user_id']
        json_date = json.loads(request.body)
        default_enable = json_date['default_enable']
        default_global_check = json_date['default_global_check']
        default_check_user = json_date['default_check_user']
        default_white_ip = json_date['default_white_ip']
        black_check_time = json_date['black_check_time']
        black_check_count = json_date['black_check_count']
        black_deny_time = json_date['black_deny_time']
        black_check = json_date['black_check']
        black_send_email = json_date['black_send_email']
        result = otp_config.objects.filter(user='admin').update(default_enable=default_enable,
                                                                default_global_check=default_global_check,
                                                                default_check_user=default_check_user,
                                                                default_white_ip=default_white_ip,
                                                                black_check_time=black_check_time,
                                                                black_check_count=black_check_count,
                                                                black_deny_time=black_deny_time,
                                                                black_check=black_check,
                                                                black_send_email=black_send_email)
        data['return_code'] = 2
        data['result'] = result
        return JsonResponse(data, safe=False)
    except:
        data['return_code'] = 0
        return JsonResponse(data, safe=False)


def send_email(request):
    data = {}
    try:
        user_id = request.session['user_id']
        json_date = json.loads(request.body)
        user_email = json_date['user_email']
        result = otp_user.objects.get(user_email=user_email)
        uri = pyotp.totp.TOTP(result.otp_secret).provisioning_uri(user_email, issuer_name="jxotp")
        buf = BytesIO()
        img = qrcode.make(uri)
        img.save(buf)
        image_stream = buf.getvalue()
        msg_image = MIMEImage(image_stream)
        msg_image.add_header('Content-ID', '<test_cid>')
        send_emails = []
        send_emails.append(user_email)
        html = '''
        <body>
        <br>请打开微信小程序，搜索 "运维密码" ，打开后 点击 "添加场景" 扫描二维码即可完成配置<br/>
        <br>详情请查看https://github.com/jx-sec/jxotp<br/>
        <img src="cid:test_cid" width="200px" height="200px"/>
        </body>
        '''
        msg = mail.EmailMessage('尊敬的的用户%s你好，请完成JXOTP动态口令设置' % (user_email), html, settings.EMAIL_HOST_USER, send_emails)
        msg.attach(msg_image)
        msg.content_subtype = 'html'
        msg.encoding = 'utf-8'
        if msg.send():
            data['return_code'] = 2
        else:
            data['return_code'] = 1
        return JsonResponse(data, safe=False)
    except:
        data['return_code'] = 0
        return JsonResponse(data, safe=False)


def log(request):
    data = {}
    try:
        mode = request.GET['mode']
        day = request.GET['day']
        user_id = request.session['user_id']
        now = datetime.now()
        aday = timedelta(days=int(day))
        if mode == '0':
            result = otp_log.objects.values('server_ip', 'client_ip', 'result', 'message', 'check_user', 'time',
                                            'user_email').filter(defalut_time__range=(now - aday, now))
            data['return_code'] = 2
            data['result'] = list(result)
            return JsonResponse(data, safe=False)
        elif mode == '1':
            result = otp_log.objects.filter(result='success').values('server_ip', 'client_ip', 'result',
                                                                     'message',
                                                                     'check_user', 'time', 'user_email').filter(
                defalut_time__range=(now - aday, now))
            data['return_code'] = 2
            data['result'] = list(result)
            return JsonResponse(data, safe=False)
        elif mode == '2':
            result = otp_log.objects.filter(result='fail').values('server_ip', 'client_ip', 'result', 'message',
                                                                  'check_user', 'time', 'user_email').filter(
                defalut_time__range=(now - aday, now))
            data['return_code'] = 2
            data['result'] = list(result)
            return JsonResponse(data, safe=False)
        elif mode == '3':
            result = otp_log.objects.filter(result='error').values('server_ip', 'client_ip', 'result',
                                                                   'message',
                                                                   'check_user', 'time', 'user_email').filter(
                defalut_time__range=(now - aday, now))
            data['return_code'] = 2
            data['result'] = list(result)
            return JsonResponse(data, safe=False)
        else:
            data['return_code'] = 1
            data['result'] = 'null'
            return JsonResponse(data, safe=False)
    except:
        data['return_code'] = 0
        return JsonResponse(data, safe=False)
