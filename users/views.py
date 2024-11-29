import re
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render

from home.models import ArticleCategory, Article
from users.models import User
from django.db import DatabaseError
from django.views import View
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from django.shortcuts import redirect
from django.urls import reverse
from utils.response_code import RETCODE
from random import randint
from libs.yuntongxun.sms import CCP
import logging

logging = logging.getLogger('django')

"""
注册的视图,继承自 View:
"""


class RegisterView(View):
    """
    用户注册接口,最重要的一步是从 Redis 中取出用户的短信验证码并校验
    """

    @staticmethod
    def get(request):
        return render(request, 'register.html')

    @staticmethod
    def post(request):
        # 接收前端传进来的参数
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        sms_code = request.POST.get('sms_code')

        # 判断参数是否齐全
        if not all([mobile, password, password2, sms_code]):
            return HttpResponseBadRequest("缺少注册信息")

        # 使用正则表达式判断手机号是否合法
        """
        - 必须以 1 开头
        - 以数字结尾
        - 第二位是 3-9 中的一个数字
        - 后面再跟9位数字
        """
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseBadRequest("请输入正确的手机号")

        """
        这里规定密码只能是8-20位的字母和数字组成的
        """
        if not re.match(r'^[a-zA-Z0-9]{8,20}$', password):
            return HttpResponseBadRequest("请输入8-20位密码")

        # 验证两次输入的密码是否一致
        if password != password2:
            return HttpResponseBadRequest("两次输入的密码不一致")

        # 验证短信验证码
        redis_conn = get_redis_connection('default')
        sms_code_server = redis_conn.get('sms:%s' % mobile)
        if sms_code_server is None:
            return HttpResponseBadRequest("短信验证码已过期")
        if sms_code_server.decode() != sms_code:
            return HttpResponseBadRequest("验证码不正确")

        # 保存注册数据
        try:
            user = User.objects.create_user(username=mobile, mobile=mobile, password=password)
        except DatabaseError:
            return HttpResponseBadRequest("注册失败")

        # 实现状态保持: 这是 Django 自带的方法,写入 session 中,之前已经配置了 Redis 中的 session,所以会自动保存到 session 中
        login(request, user)

        # return HttpResponse('注册成功重定向到首页')
        # 重定向到首页, 可以通过 namespace:name 获取视图对应的路由,这就是定义命名空间的好处
        response = redirect(reverse('home:index'))

        # 设置 cookie, 以便于主页获取, 保存登陆状态
        response.set_cookie('is_login', True)

        # 设置用户名的有效期为一个月
        response.set_cookie('username', user.username, max_age=30 * 24 * 3600)
        return response


class CaptchaView(View):
    """
    图片验证码接口,前端 JS 调用
    """

    @staticmethod
    def get(request):
        """
        生成验证码并且存储到 Redis 中
        :param request: 请求对象
        :return: 返回值,这里是一个响应对象
        """
        # 首先从前端获取到验证码的 uuid
        uuid = request.GET.get('uuid')

        # 然后做一个判断,确保 UUID 存在
        if uuid is None:
            return HttpResponseBadRequest("验证码有误!")

        # 通过验证码库生成验证码
        text, image = captcha.generate_captcha()

        # 获取 Redis 连接
        redis_conn = get_redis_connection("default")

        # 存入 Redis 中, (键, 存活时间, 值) 300s = 5分钟
        redis_conn.setex("img:%s" % uuid, 300, text)

        # 返回给前端验证码图片
        return HttpResponse(image, content_type="image/jpeg")


class SmsCodeView(View):
    """
    手机短信验证码接口, 前端 JS 调用
    """

    @staticmethod
    def get(request):
        # 接收前端传入的参数
        image_code_client = request.GET.get('image_code')
        uuid = request.GET.get('uuid')
        mobile = request.GET.get('mobile')

        # 校验参数
        if not all([image_code_client, uuid, mobile]):
            return HttpResponseBadRequest('缺少必要参数')

        # 创建连接到 redis 的对象
        redis_conn = get_redis_connection('default')

        # 提取图片验证码
        image_code_server = redis_conn.get('img:%s' % uuid)

        if image_code_server is None:
            # 图片验证码过期或者不存在
            return JsonResponse({'code': RETCODE.IMAGECODEERR,
                                 'errmsg': '图形验证码失效'})

        # 删除图形验证码
        try:
            redis_conn.delete('img:%s' % uuid)
        except Exception as e:
            logging.error(e)

        """
            先对比图形验证码是否正确:
                因为如果图形都不对就不需要对比手机了.
        """
        # 比特转字符串
        image_code_server = image_code_server.decode()
        # 转成小写之后再比较
        if image_code_client.lower() != image_code_server.lower():
            return JsonResponse({'code': RETCODE.IMAGECODEERR,
                                 'errmsg': '输入的图形验证码有误'})

        """
            用 Random 库生成随机的手机验证码,然后存储到 Redis 中,同时在控制台打印输出,方便调试
            最后调用 '容联云' 的接口发送验证码:
                注意目前这里只能向我指定的手机号发送验证码. 17858918830
        """
        # 随机生成 6 位验证码
        sms_code = '%06d' % randint(0, 999999)

        # 将验证码输出到控制台
        logging.info(sms_code)
        # 保存到 Redis 中
        redis_conn.setex('sms:%s' % mobile, 300, sms_code)

        # 发送短信 17858918830;
        # 参数一是手机号;
        # 参数二是模板中的内容, 您的验证码为 1234, 请于 5 分钟之内填写;
        # 参数三是短信模板,用于测试只能是1.
        CCP().send_template_sms(mobile, [sms_code, 5], 1)

        # 响应结果
        return JsonResponse({'code': RETCODE.OK,
                             'errmsg': '发送短信成功'})


class LoginView(View):
    """
    登陆接口
    """

    @staticmethod
    def get(request):
        return render(request, 'login.html')

    @staticmethod
    def post(request):
        # 获取请求参数
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        remember = request.POST.get('remember')

        # 校验参数, 判断是否齐全
        if not all([mobile, password]):
            return HttpResponseBadRequest('缺少请求参数')

        # 判断具体的参数是否正确
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseBadRequest('请输入正确的手机号')
        if not re.match(r'^[0-9a-zA-Z]{8,20}$', password):
            return HttpResponseBadRequest('密码最少8位,最多20位')

        # 认证登陆的用户: authenticate 是 Django 自带的认证方法
        user = authenticate(mobile=mobile, password=password)

        if user is None:
            return HttpResponseBadRequest('用户名或者密码错误')

        # 实现登陆状态保持
        login(request, user)

        # 根据 next 参数来进行页面的跳转: 由用户信息页面传递的参数
        nex = request.GET.get('next')
        if nex:
            response = redirect(nex)
        else:
            response = redirect(reverse('home:index'))

        # 存储到 Cookie 中
        if remember != 'on':
            # 用户没有选择记住我,浏览区会话结束就过期
            request.session.set_expiry(0)
            response.set_cookie('is_login', True)
            response.set_cookie('username', user.username, max_age=30 * 24 * 3600)
        else:
            # 用户选择了记住我: set_expiry 默认两周之后过期
            request.session.set_expiry(None)
            response.set_cookie('is_login', True, max_age=14 * 24 * 3600)
            response.set_cookie('username', user.username, max_age=30 * 24 * 3600)

        # 返回响应
        return response


class LogoutView(View):
    """
    退出登陆:
        - 清理 session
        - 清理 cookie
    """

    @staticmethod
    def get(request):
        # logout 为 Django 自带的登出方法,它封装了清理 session 的操作
        logout(request)
        response = redirect(reverse('home:index'))
        response.delete_cookie('is_login')
        response.delete_cookie('username')
        return response


class ForgetPasswordView(View):
    """
    忘记密码接口
    """

    @staticmethod
    def get(request):
        return render(request, 'forget_password.html')

    @staticmethod
    def post(request):
        # 接收前端的参数
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        sms_code = request.POST.get('sms_code')

        # 判断普通参数的完整性和正确性
        if not all([mobile, password, password2, sms_code]):
            return HttpResponseBadRequest('缺少参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseBadRequest('请输入正确的手机号')
        if not re.match(r'^[0-9a-zA-Z]{8,20}$', password):
            return HttpResponseBadRequest('请输入8-20位密码')
        if password2 != password:
            return HttpResponseBadRequest('两次输入的密码不一致')

        # 判断手机验证码的正确性
        redis_conn = get_redis_connection('default')
        sms_code_server = redis_conn.get('sms:%s' % mobile)
        if sms_code_server is None:
            return HttpResponseBadRequest('短信验证码已过期')
        if sms_code != sms_code_server.decode():
            return HttpResponseBadRequest('短信验证码错误')

        # 根据手机号码查询数据
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            # 如果不存在就注册一个新的用户
            try:
                User.objects.create_user(username=mobile, mobile=mobile, password=password)
            except Exception:
                return HttpResponseBadRequest('修改失败,请稍后重试!')
        else:
            # 用户存在,修改密码
            user.set_password(password)
            user.save()

        # 跳转到登录页面
        return redirect(reverse('users:login'))


class UserCenterView(LoginRequiredMixin, View):
    """
    用户个人信息的展示与修改
    """

    @staticmethod
    def get(request):
        """
        获取用户信息并渲染到页面中
        :param request: 请求对象
        :return: 返回页面和数据信息
        """
        # 获取用户信息
        user = request.user

        # 将数据渲染到页面上
        context = {
            'username': user.username,
            'mobile': user.mobile,
            'avatar': user.avatar.url if user.avatar else None,
            'user_desc': user.user_desc
        }
        return render(request, 'center.html', context=context)

    @staticmethod
    def post(request):
        # 接收前端传过来的数据
        user = request.user
        avatar = request.FILES.get('avatar')
        username = request.POST.get('username')
        user_desc = request.POST.get('desc', user.user_desc)

        # 修改数据库中的数据
        try:
            user.username = username
            user.user_desc = user_desc
            if avatar:
                user.avatar = avatar
            user.save()
        except Exception as e:
            logging.error(e)
            return HttpResponseBadRequest('更新失败,请稍后再试')

        # 返回响应
        response = redirect(reverse('users:center'))

        # 更新 cookie 信息
        response.set_cookie('username', user.username, max_age=30 * 24 * 3600)
        return response


class WriteBlogView(View):
    """
    写博客的页面展示接口
    """

    @staticmethod
    def get(request):
        """
        将文章分类信息传递给写博客页面
        :param request: 请求
        :return: 返回写博客页面
        """
        # 获取文章分类信息: 查询所有
        categories = ArticleCategory.objects.all()

        context = {
            'categories': categories
        }
        return render(request, 'write_blog.html', context=context)

    @staticmethod
    def post(request):
        """
        接收前端的 POST 请求: 将数据保存到数据库
        :param request: 请求
        :return: 返回响应
        """
        # 接收数据
        avatar = request.FILES.get('avatar')
        title = request.POST.get('title')
        category_id = request.POST.get('category')
        tags = request.POST.get('tags')
        summary = request.POST.get('summary')
        content = request.POST.get('content')
        user = request.user

        # 验证数据是否齐全
        if not all([avatar, title, category_id, summary, content]):
            return HttpResponseBadRequest('参数不全')

        # 判断文章分类的 ID 是否正确
        try:
            article_category = ArticleCategory.objects.get(id=category_id)
        except ArticleCategory.DoesNotExist:
            return HttpResponseBadRequest('没有此分类信息')

        # 保存到数据库
        try:
            article = Article.objects.create(
                author=user,
                avatar=avatar,
                category=article_category,
                tags=tags,
                title=title,
                summary=summary,
                content=content
            )
        except Exception as e:
            logging.error(e)
            return HttpResponseBadRequest('发布失败,请稍后再试')

        # 返回响应: 跳转到首页
        return redirect(reverse('home:index'))
        pass
