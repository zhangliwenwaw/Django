from django.contrib import admin

# Register your models here.
from home.models import ArticleCategory

# 导入模型类: 注册
admin.site.register(ArticleCategory)
