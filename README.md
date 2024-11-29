Blog_Django
---
![](https://img-blog.csdnimg.cn/20200613191600362.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl80Mzk0MTM2NA==,size_16,color_FFFFFF,t_70)
![](https://img-blog.csdnimg.cn/20200614085714357.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl80Mzk0MTM2NA==,size_16,color_FFFFFF,t_70)

### 项目介绍
使用 `Django` 框架开发的个人博客网站：网站按照用户进行区分，用户为独立创作者可以自由发布文章，同时任何人都可以看到其他所有人的文章，只以作者作为区分。

主要有以下几个特色功能:
- 注册时使用图片验证码+手机验证码的方式认证，同时密码加密存储，保证安全性;
- 可以直接在网页上写博客，内置 HTML 文本编辑器；
- 博客有分类功能、留言功能、按照热度自动推荐功能、同时有浏览数量和浏览数量的记录；

### 技术亮点
1. 采用 `Vue` 作为前端框架
2. 采用 `Django` 作为后端框架
3. 采用 `Django` 模板引擎
4. 采用云通讯短信发送
5. 采用 `session` 技术
### 语言及工具版本
- `Python 3.6`
- `MySQL 5.7`
- `Django 3.0` 
- `Redis 3.2` 

### 项目结构介绍
- `home` 为子应用：管理博客和评论
- `libs` 为依赖的第三方库：图片验证码和手机号短信验证码；
- `logs` 没传上来：用于日志输出；
- `media` 媒体资源文件：头像图片之类的；
- `my_blog` 主应用：用于注册其它应用，设置超级管理员等；
- `static` 静态资源目录：js 和 css 等；
- `template` 模板引擎文件夹：就是几个主页面；
- `users` 用户子应用：用于实现用户登陆等功能；
- `utils` 工具类包：自定义装填码信息； 

### 如何启动

```bash
# 一般大家能找到这个项目肯定都安装了 python 和 Django 的环境,还需要下面几个库
pip install pymysql
pip install django-redis
pip install Pillow
```

1. 去项目的 `/my_blog/settings.py` 文件下修改 `DATABASES` 配置信息：包括数据库的用户名和密码；
2. 首先执行 `sql` 建库：或者在项目内执行 `migrate` 命令，但是这样的话你的数据库是空的，啥都没有；
3. 配置好本地的 `Redis` 环境: 启动 `server` 即可；
4. 直接启动项目即可：本项目的开发环境为 `win10`

### 注意事项

1. 获取短信验证码使用的是 `容联云` 的接口：因为他是免费测试使用的，所以只能使用我的手机号注册：17858918830 ；由于是开发阶段，所以我将验证码打印在了控制台，你也可以直接将控制台的输出填到验证码上完成注册；
2. 请注意这个 `API` 使用的别人的接口，所以如果你想实际使用请到官网注册账号，然后将你的密钥的键值对和应用 ID 填写到项目的 `libs/yuntongxun/sms.py` 文件中的指定位置；
3. 另外就算是注册成功了，他发送短信也很慢，因为是免费的接口；


### 测试用户
如果你不想注册了，那就可以使用下面几个用户体验一下
- `test` 
用户名: `17858918832` 
密码: `1111111111` (10个1)

- `admin`
用户名: `17858918831`
密码: `wsuo2821`

其中  `admin` 为超级管理员用户，用于登陆 `Django` 自带的 `admin` 后台管理系统； <br>


### 待完善功能
有些功能因为时间关系还没做，等以后闲了再补上，主要是内容很简单，相信大家能看懂这些代码肯定也能自己实现下面的功能：
- 增加删除修改文章功能；
- 增加用户管理；
- 优化前端展示页面（这个页面目前有点丑，是我随便找的一个模板然后加上 `vuejs` 就拿来用了）
- ······
