"""BBS01 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from django.views.static import serve

from BBS01 import settings
from app01 import views

urlpatterns = [
    path("admin/", admin.site.urls),
    # 注册
    path("register/", views.register, name='reg'),
    # 登录
    path("login/", views.login, name='login'),
    # 图片验证码
    path("get_code/", views.get_code),
    # 首页
    path("home/", views.home, name='home'),
    # 修改密码
    path("set_password/", views.set_password, name='set_pwd'),
    # 退出登录
    path("logout/", views.logout, name='logout'),
    # 暴露后端指定文件夹资源
    re_path("media/(?P<path>.*)", serve, {'document_root': settings.MEDIA_ROOT}),
    # 点赞点踩
    re_path("up_or_down", views.up_or_down, name='up_or_down'),
    # 文章评论
    re_path("comment", views.comment, name='comment'),
    # 后台管理
    re_path("backend", views.backend, name='backend'),
    # 添加文章
    re_path("add/article", views.add_article, name='add_article'),
    # 删除文章
    re_path("delete_article", views.delete_article, name='delete_article'),
    # 编辑器上传图片
    re_path("upload_image", views.upload_image, name='upload_image'),
    # 修改用户头像
    re_path("set/avatar", views.set_avatar, name='set_avatar'),
    # 个人站点页面搭建
    re_path("^(?P<username>\w+)/$", views.site, name='site'),
    # 侧边栏筛选功能
    re_path(r"^(?P<username>\w+)/(?P<condition>category|tag|archive)/(?P<param>.*)/", views.site),
    # 文章详情页
    re_path(r"^(?P<username>\w+)/article/(?P<article_id>\d+)/", views.article_detail),
]
