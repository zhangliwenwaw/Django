from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

"""
    自定义一个用户类 User 继承自 AbstractUser(Django 自带的用户类):
        但是该类中缺少:
            - 手机号
            - 头像
            - 简介
        所以我们扩展该类
"""


class User(AbstractUser):
    # 手机号(长度为11, 唯一, 不为空)
    mobile = models.CharField(max_length=11, unique=True, blank=False)

    # 头像信息(图片类型的, 保存到项目目录下的 avatar 文件夹下_以日期创建文件夹区分, 可以为空)
    avatar = models.ImageField(upload_to='avatar/%Y%m%d/', blank=True)

    # 简介信息(最大长度为500, 可以为空)
    user_desc = models.CharField(max_length=500, blank=True)

    class Meta:
        # 修改表名
        db_table = 'tb_users'
        # 设置后台管理显示的名称
        verbose_name = '用户管理'
        # admin 后台显示
        verbose_name_plural = verbose_name

    # 重写 str 方法
    def __str__(self):
        return self.mobile

    # 默认的认证方法中是对username进行认证。我们需要修改认证的字段为mobile。
    # 所以我们需要在User的模型中修改
    USERNAME_FIELD = 'mobile'

    # 创建管理员所必须的字段: 用户名和邮箱
    REQUIRED_FIELDS = ['username', 'email']
