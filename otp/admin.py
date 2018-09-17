from django.contrib import admin
from models import *


# Register your models here.

class server(admin.ModelAdmin):
    list_display = ('server_ip', 'enable', 'custom', 'global_check', 'check_user', 'white_ip')


class user(admin.ModelAdmin):
    list_display = ('user_email', 'otp_secret', 'enable')


class config(admin.ModelAdmin):
    list_display = ('user','default_enable', 'default_global_check', 'default_check_user', 'default_white_ip', 'black_check',
                    'black_send_email', 'black_deny_time', 'black_check_count', 'black_check_time')


class log(admin.ModelAdmin):
    list_display = ('server_ip', 'client_ip', 'result', 'message', 'check_user', 'defalut_time', 'user_email')

class alert(admin.ModelAdmin):
    list_display = ('client_ip', 'server_ip', 'time', 'defalut_time')

admin.site.register(otp_server, server)
admin.site.register(otp_user, user)
admin.site.register(otp_config, config)
admin.site.register(otp_log, log)
admin.site.register(otp_alert, alert)