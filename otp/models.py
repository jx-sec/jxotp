from __future__ import unicode_literals

from django.db import models
from django.utils import timezone


# Create your models here.
class otp_server(models.Model):
    server_ip = models.CharField(unique=True, max_length=50)
    enable = models.CharField(default='true', max_length=50)
    custom = models.CharField(default='false', max_length=50)
    global_check = models.CharField(default='false', max_length=50)
    check_user = models.CharField(default='root', max_length=50)
    white_ip = models.CharField(default='YOU BYPASS IP', max_length=50)

    # check_email = models.CharField(default='false', max_length=50)
    # user_email = models.CharField(default='check user email', max_length=50)

    def __unicode__(self):
        return str(self.server_ip)


class otp_config(models.Model):
    user = models.CharField(default='admin', max_length=50)
    default_enable = models.CharField(default='true', max_length=50)
    default_global_check = models.CharField(default='false', max_length=50)
    default_check_user = models.CharField(default='root', max_length=50)
    default_white_ip = models.CharField(default='YOU BYPASS IP', max_length=50)
    black_check = models.CharField(default='false', max_length=50)
    black_check_time = models.CharField(default='5', max_length=50)
    black_check_count = models.CharField(default='10', max_length=50)
    black_deny_time = models.CharField(default='30', max_length=50)
    black_send_email = models.CharField(default='false', max_length=100)

    def __unicode__(self):
        return str(self.user)


class otp_user(models.Model):
    user_email = models.CharField(default='false', max_length=50, unique=True)
    otp_secret = models.CharField(default='false', max_length=100)
    enable = models.CharField(default='true', max_length=50)

    def __unicode__(self):
        return str(self.user_email)


class otp_log(models.Model):
    server_ip = models.CharField(default='false', max_length=50)
    client_ip = models.CharField(default='false', max_length=50)
    result = models.CharField(default='false', max_length=50)
    message = models.CharField(default='false', max_length=50)
    check_user = models.CharField(default='false', max_length=50)
    time = models.CharField(default='false', max_length=50)
    defalut_time = models.DateTimeField(default=timezone.now)
    user_email = models.CharField(default='false', max_length=50)


class otp_alert(models.Model):
    client_ip = models.CharField(default='false', max_length=50)
    server_ip = models.CharField(default='false', max_length=50)
    time = models.DateTimeField(default=timezone.now)
    defalut_time = models.DateTimeField(default=timezone.now)
