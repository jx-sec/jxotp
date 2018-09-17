"""jxotp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from otp.views import *
from django.conf import settings

urlpatterns = [
    url(r'^$', index),
    #url(r'^(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
    #url(r'^admin/', admin.site.urls),
    url(r'^otp_auth$', otp_auth),
    url(r'^api/login$', login),
    url(r'^api/logout$', logout),
    url(r'^api/user_add$', user_add),
    url(r'^api/user_del$', user_del),
    url(r'^api/user_list$', user_list),
    url(r'^api/server_add$', server_add),
    url(r'^api/server_del$', server_del),
    url(r'^api/server_list$', server_list),
    url(r'^api/config_list$', config_list),
    url(r'^api/config_add$', config_add),
    url(r'^api/send_email$', send_email),
    url(r'^api/log$', log),
]
