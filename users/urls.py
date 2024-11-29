"""
@author: shoo Wang
@contact: wangsuoo@foxmail.com
@file: urls.py
@time: 2020/6/11 0011
"""
"""
用于定义 Users 子应用的路由
"""

from django.urls import path
from users.views import RegisterView, CaptchaView, SmsCodeView, LoginView, LogoutView, ForgetPasswordView, \
    UserCenterView, WriteBlogView

urlpatterns = [

    # path(路由, 视图函数名)
    path('register/', RegisterView.as_view(), name='register'),

    # 图片验证码的路由
    path('imagecode/', CaptchaView.as_view(), name='imagecode'),

    # 手机验证码的路由
    path('smscode/', SmsCodeView.as_view(), name='smscode'),

    # 登陆的路由
    path('login/', LoginView.as_view(), name='login'),

    # 退出登陆
    path('logout/', LogoutView.as_view(), name='logout'),

    # 忘记密码
    path('forgetpassword/', ForgetPasswordView.as_view(), name='forgetpassword'),

    # 用户个人信息页面
    path('center/', UserCenterView.as_view(), name='center'),

    # 写文章的路由
    path('writeblog/', WriteBlogView.as_view(), name='writeblog'),
]
