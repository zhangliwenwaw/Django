from django.core.paginator import Paginator, EmptyPage
from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View

# Create your views here.
from home.models import ArticleCategory, Article, Comment


class IndexView(View):
    """
    首页展示
    """

    @staticmethod
    def get(request):
        """
        首页数据
        :param request: 请求对象
        :return: 返回视图
        """
        cat_id = request.GET.get('cat_id', 1)
        page_num = request.GET.get('page_num', 1)
        page_size = request.GET.get('page_size', 10)

        # 判断分类 ID
        try:
            category = ArticleCategory.objects.get(id=cat_id)
        except ArticleCategory.DoesNotExist:
            return HttpResponseNotFound('没有此分类')

        # 获取博客的分类信息
        categories = ArticleCategory.objects.all()

        # 分页数据
        articles = Article.objects.filter(
            category=category
        )

        # 创建分页器: 分页N条记录
        paginator = Paginator(articles, per_page=page_size)
        # 获取每页的数据
        try:
            page_article = paginator.page(page_num)
        except EmptyPage:
            # 如果没有分页数据: 默认 404
            return HttpResponseNotFound('404 page')

        # 获取列表总页数
        total_page = paginator.num_pages

        context = {
            'categories': categories,
            'category': category,
            'articles': page_article,
            'page_size': page_size,
            'total_page': total_page,
            'page_num': page_num,
        }

        return render(request, 'index.html', context=context)


class DetailView(View):
    """
    文章详情展示
    """

    @staticmethod
    def get(request):
        """
        查询文章数据通过 context 传递给 detail 页面
        :param request: 请求
        :return: 返回 context
        """
        aid = request.GET.get('id')
        page_num = request.GET.get('page_num', 1)
        page_size = request.GET.get('page_size', 5)
        categories = ArticleCategory.objects.all()
        try:
            article = Article.objects.get(id=aid)
        except Article.DoesNotExist:
            return render(request, '404.html')
        else:
            # 每次访问都给文章的浏览量加1
            article.total_view += 1
            article.save()

        # 根据之前的浏览数设置推荐文章: 推荐那些浏览量高的文章
        hot_articles = Article.objects.order_by('-total_view')[:9]

        # 获取该文章的评论信息
        comments = Comment.objects.filter(
            article=article
        ).order_by('-created')

        # 获取评论总数
        total_count = comments.count()

        # 创建分页器：分页展示评论数据
        paginator = Paginator(comments, page_size)
        # 获取每页评论数据
        try:
            page_comments = paginator.page(page_num)
        except EmptyPage:
            # 如果page_num不正确，默认给用户404
            return HttpResponseNotFound('404 page')
        # 获取评论的总页数
        total_page = paginator.num_pages

        context = {
            'categories': categories,
            'category': article.category,
            'article': article,
            'hot_articles': hot_articles,
            'total_count': total_count,
            'comments': page_comments,
            'page_size': page_size,
            'total_page': total_page,
            'page_num': page_num,
        }

        return render(request, 'detail.html', context=context)

    @staticmethod
    def post(request):
        # 获取用户信息
        user = request.user

        # 判断用户是否登陆
        if user and user.is_authenticated:
            # 接收数据
            aid = request.POST.get('id')
            content = request.POST.get('content')

            # 判断文章是否存在
            try:
                article = Article.objects.get(id=aid)
            except Article.DoesNotExist:
                return HttpResponseNotFound('没有此文章')

            # 保存到数据库
            comment = Comment.objects.create(content=content, user=user, article=article)

            # 修改文章的评论数量
            article.comments_count += 1
            article.save()

            # 拼接跳转路由
            path = reverse('home:detail') + '?id={}'.format(article.id)
            return redirect(path)
        else:
            # 没有登陆则跳转到登陆页面
            return redirect(reverse('users:login'))
