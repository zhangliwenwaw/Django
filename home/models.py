from django.db import models
from django.utils import timezone

from users.models import User


class ArticleCategory(models.Model):
    """
    文章分类实体类
    """
    # 栏目标题
    title = models.CharField(max_length=100, blank=True)
    # 创建时间
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        """
        重写该方法: 页面中才可以显示
        :return: 返回标题即可
        """
        return self.title

    class Meta:
        db_table = 'tb_category'
        verbose_name = '类别管理'
        verbose_name_plural = verbose_name


class Article(models.Model):
    """
    文章实体类
    """
    # 外键约束: 和用户表关联在一起: 设置级联删除: 即删除用户的同时会删除该用户的所有文章
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    # 文章标题图: 图片类型的, 保存到项目目录下的 article 文件夹下_以日期创建文件夹区分, 可以为空
    avatar = models.ImageField(upload_to='article/%Y%m%d/', blank=True)

    # 文章栏目是 "一对多" 外键: 一个栏目对应多个文章
    category = models.ForeignKey(
        ArticleCategory,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='article'
    )

    # 文章标签
    tags = models.CharField(max_length=20, blank=True)

    # 文章标题
    title = models.CharField(max_length=100, null=False, blank=False)

    # 概要
    summary = models.CharField(max_length=200, null=False, blank=False)

    # 文章正文
    content = models.TextField()

    # 浏览量: 正整数
    total_view = models.PositiveIntegerField(default=0)

    # 文章评论数
    comments_count = models.PositiveIntegerField(default=0)

    # 文章创建时间: 默认写当前的时间
    created = models.DateTimeField(default=timezone.now)

    # 文章更新时间: 自动写入当前时间
    updated = models.DateTimeField(auto_now=True)

    # 指定创建数据库表的规则
    class Meta:
        # ordering 指定排序规则: 倒序
        ordering = ('-created',)
        db_table = 'tb_article'
        verbose_name = '文章管理'
        verbose_name_plural = verbose_name

    def __str__(self):
        """
        重写方法: 方便后台管理的显示: 更易读
        :return: 返回值
        """
        return self.title


class Comment(models.Model):
    """
    评论实体类
    """
    # 评论内容
    content = models.TextField()
    # 评论的文章
    article = models.ForeignKey(Article, on_delete=models.SET_NULL, null=True)
    # 发表评论的用户
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
    # 评论时间
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.article.title

    class Meta:
        db_table = 'tb_comment'
        verbose_name = '评论管理'
        verbose_name_plural = verbose_name
