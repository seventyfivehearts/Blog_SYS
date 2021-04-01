"""BBS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
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
from app01 import views
from django.views.static import serve
from BBS import settings
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    # 注册页面
    url(r'^register/', views.register, name='reg'),
    # 登录功能
    url(r'^login/', views.login, name='login'),
    # 图片相关
    url(r'^get_code/', views.get_code),
    # 首页
    url(r'^home/', views.home, name='home'),

    # 修改密码
    url(r'^set_password/', views.set_password, name='set_pwd'),
    # 退出登录
    url(r'^logout/', views.logout, name='logout'),

    # 暴露后端文件指定文件资源
    url(r'^media/(?P<path>.*)', serve, {'document_root':settings.MEDIA_ROOT}),

    # 个人站点页面搭建
    url(r'^(?P<username>\w+)/$', views.site, name='site'),
]
