"""
@author: shoo Wang
@contact: wangsuoo@foxmail.com
@file: urls.py
@time: 2020/6/12 0012
"""

from django.urls import path
from home.views import IndexView, DetailView

urlpatterns = [
    # 首页的路由 即什么路径都不写就会跳转到首页
    path('', IndexView.as_view(), name='index'),
    path('detail/', DetailView.as_view(), name='detail'),
]
