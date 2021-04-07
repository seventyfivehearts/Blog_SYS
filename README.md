# BBS 前端和后端不分离的项目，前后端都需要自己完成

## 表创建同步

```python
# 数据库使用MySQL 由于django自带的数据库对时间不敏感

# 数据库设置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'BBS',
        'USER': 'root',
        'PASSWORD': 'root123',
        'HOST': '127.0.0.1',
        'PORT': 3306,
        'CHARSET': 'utf8',
    }
}

# 在任意__init__文件下书写
import pymysql
pymysql.install_as_MySQLdb()
```

## model.py

```python
from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

"""
先写基础字段
再写外键字段
"""


class UserInfo(AbstractUser):
    phone = models.BigIntegerField(verbose_name='用户手机号', null=True)
    # 用户头像
    avatar = models.FileField(upload_to='avatar/', default='avatar/default.png', verbose_name='创建时间')
    """
    给avatar字段传文件对象，文件会自动保存到avatar/目录下，默认是default.png图片
    """
    # 创建时间
    create_time = models.DateField(auto_now_add=True)

    # 一对一
    blog = models.OneToOneField(to='Blog', null=True)


class Blog(models.Model):
    site_name = models.CharField(max_length=32, verbose_name='站点名称')
    site_title = models.CharField(max_length=32, verbose_name='站点标题')
    site_theme = models.CharField(max_length=64, verbose_name='站点样式(主题)')  # 存放css/js的文件路径


class Category(models.Model):
    name = models.CharField(max_length=32, verbose_name='文章分类')
    # 一对多
    blog = models.ForeignKey(to='Blog', null=True)


class Tag(models.Model):
    name = models.CharField(max_length=32, verbose_name='文章标签')
    # 一对多
    blog = models.ForeignKey(to='Blog', null=True)


class Article(models.Model):
    title = models.CharField(max_length=64, verbose_name='文章标题')
    desc = models.CharField(max_length=255, verbose_name='文章简介')
    #   文章内容一般使用TextField
    content = models.TextField(verbose_name='文章内容')

    # 数据库字段优化
    up_num = models.BigIntegerField(default=0, verbose_name='点赞数')
    down_num = models.BigIntegerField(default=0, verbose_name='点踩数')
    comment_num = models.BigIntegerField(default=0, verbose_name='评论数')
    # 外键字段
    blog = models.ForeignKey(to='Blog', null=True)
    category = models.ForeignKey(to='Category', null=True)
    tags = models.ManyToManyField(to='Tag',
                                  through='Article2Tag',
                                  through_fields=('article', 'tag'))


class Article2Tag(models.Model):
    article = models.ForeignKey(to='Article')
    tag = models.ForeignKey(to='Tag')


class UpAndDown(models.Model):
    user = models.ForeignKey(to='UserInfo')
    article = models.ForeignKey(to='Article')
    content = models.CharField(max_length=255, verbose_name='评论内容')
    comment_time = models.DateField(auto_now_add=True, verbose_name='评论时间')
    # 自评论
    parent = models.ForeignKey(to='self')  # 有些评论为根评论

```



## 注册功能

```python
"""
为了解耦合 如果项目中只用到了一个forms组件，创建一个即可
	myforms.py
	
如果使用到了多个，可以创建一个文件夹，根据组件功能的不同创建不同的py文件
	regforms.py
	loginforms.py
	userforms.py
"""
<div class="container-fluid">
    <div class="row">
        <div class="col-md-8 col-md-offset-2">
            <h1 class="text-center">注册</h1>
            <form id="myform">
                {% csrf_token %}
                {% for form in form_obj %}
                    <div class="form-group">
                        <label for="">{{ form.label }}</label>
                        {{ form }}
                        <span style="color: red">{{ form.errors.0 }}</span>
                    </div>
                {% endfor %}
                
            </form>

        </div>
    </div>
</div>
```



## forms组件

```python
# 针对用户表的forms组件
from django import forms
from app01 import models


class MyRegForm(forms.Form):
    username = forms.CharField(label='用户名', min_length=3, max_length=8,
                               error_messages={
                                   'required': '用户名不能为空',
                                   'min_length': '用户名最小为三位',
                                   'max_length': '用户名最大为八位',
                               },
                               # 需要让标签有bootstrap样式
                               # widget=forms.widgets.TextInput(attrs={'class': 'form-control'}),
                               widget = forms.widgets.TextInput(attrs={'class': 'form-control '}),
                               )
    password = forms.CharField(label='密码', min_length=3, max_length=8,
                               error_messages={
                                   'required': '密码不能为空',
                                   'min_length': '密码最小为三位',
                                   'max_length': '密码最大为八位',
                               },
                               # 需要让标签有bootstrap样式
                               widget = forms.widgets.PasswordInput(attrs={'class': 'form-control'})
                               )
    confirm_password = forms.CharField(label='确认密码', min_length=3, max_length=8,
                                       error_messages={
                                           'required': '确认密码不能为空',
                                           'min_length': '确认密码最小为三位',
                                           'max_length': '确认密码最大为八位',
                                       },
                                       # 需要让标签有bootstrap样式
                                       widget=forms.widgets.PasswordInput(attrs={'class': 'form-control'})
                                       )
    email = forms.EmailField(label='邮箱',
                             error_messages={
                                 'required': '邮箱不能为空',
                                 'invalid': '邮箱格式不正确',
                             },
                             widget=forms.widgets.EmailInput(attrs={'class': 'form-control'})
                             )

    # 钩子函数
    # 局部钩子： 校验用户名是否存在
    def clean_username(self):
        username = self.cleaned_data.get('username')
        # 去数据库校验
        is_exist = models.UserInfo.objects.filter(username=username)
        if is_exist:
            self.add_error('username', '用户名已存在')
            # 使用钩子函数要把参数还回去
        return username

    # 全局钩子  校验两次用户名是否一致
    def clean(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_data')
        if not password == confirm_password:
            self.add_error('confirm_password', '两次输入的密码不一样')

        return self.cleaned_data

```



## 用户头像前端实时展现

```python
# 静态文件配置
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]
```

# 出现的问题

用户头像修改之后在前端展示的时候不显示

```python
# 解决办法
myFileReaderObj.readAsDataURL(fileObj); //异步操作 图片未读取完毕，代码执行到下一步
 myFileReaderObj.onload = function(){
            $('#myimg').attr('src', myFileReaderObj.result)
        }

      //文件阅读器
        //1.先生成一个文件阅读器对象
        let myFileReaderObj = new FileReader();
        //2.获取用户上传信息
        let fileObj = $(this)[0].files[0]; 
        //3.将文件对象交给阅读器对象读取
        myFileReaderObj.readAsDataURL(fileObj); //异步操作 图片未读取完毕，代码执行到下一步
        //4.利用文件阅读器将文件展示到前端页面 修改src属性
        // 等待文件阅读器加载完毕之后再执行
        myFileReaderObj.onload = function(){
            $('#myimg').attr('src', myFileReaderObj.result)
        }
# 修改图片不显示
解决办法读取文件有问题 不应该是file 是files
 let fileObj = $(this)[0].files[0];
```

```python
注册之后跳转到登录界面
```

## 图片验证码

```python
<img src="/get_code/" alt="" width="380" height="35">
# 前端设置点击事件完成刷新功能 
<script>
    $('#id_img').click(function () {
        //1.获取标签之间的src
        let oldVal = $(this).attr('src')
        $(this).attr('src', oldVal += '?')
    })
</script>

def get_code(request):
    # 方式1 直接获取后端现成的图片二进制数据发送给前端
    # with open(r'static/img/1.jpg', 'rb') as f:
    #     data = f.read()
    # return HttpResponse(data)
    # 方式二 利用pillow模块动态产生图片
    # img_obj = Image.new('RGB', (380, 35), get_random())
    # # 先将图片对象保存起来
    # with open('xx.png', 'wb') as f:
    #     img_obj.save(f, 'png')
    # # 在将图片对象读取出来
    # with open('xx.png', 'rb') as f:
    #     data = f.read()
    # return HttpResponse(data)
    # 方法三 文件存储繁琐IO操作效率低 借助于内存管理器模块
    # img_obj = Image.new('RGB', (380, 35), get_random())
    # io_obj = BytesIO()  # 生成一个内存管理对象
    # img_obj.save(io_obj, 'png')
    # return HttpResponse(io_obj.getvalue())  # 从内存管理器中读取的二进制图片数据返回给前端
    # 最终方案
    img_obj = Image.new('RGB', (380, 35), get_random())
    img_draw = ImageDraw.Draw(img_obj)
    img_font = ImageFont.truetype('static/font/albbhpzt.ttf', 30)  # 字体样式 大小

    # 随机验证码 五位数的随机验证码 数字 小写字母 大写字母
    code = ''
    for i in range(5):
        random_upper = chr(random.randint(65, 90))
        random_lower = chr(random.randint(97, 122))
        random_int = str(random.randint(0, 9))
        # 从上面随机选择一个写到图片上
        tmp = random.choice([random_lower, random_upper, random_int])
        img_draw.text((i*60 + 60, -2), tmp, get_random(), img_font)
        code += tmp
    print(code)
    request.session['code'] = code
    io_obj = BytesIO()
    img_obj.save(io_obj, 'png')
    return HttpResponse(io_obj.getvalue())

```

## 登录功能

```python
# 后端
def login(request):
    back_dir = {'code': 1000, 'msg': ''}
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        code = request.POST.get('code')
        # 1.先校验验证码是否正确 统一转大写或小写
        if request.session.get('code').upper() == code.upper():
            # 2.校验用户名或密码是否正确
            user_obj = auth.authenticate(request, username=username, password=password)
            if user_obj:
                auth.login(request, user_obj)
                back_dir['url'] = '/home/'
            else:
                back_dir['code'] = 2000
                back_dir['msg'] = '用户名或密码错误'
        else:
            back_dir['code'] = 3000
            back_dir['msg'] = '验证码错误'
        return JsonResponse(back_dir)
    return render(request, 'login.html')
#前端
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.bootcdn.net/ajax/libs/twitter-bootstrap/3.4.1/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.bootcdn.net/ajax/libs/jquery/3.4.1/jquery.min.js"></script>
    <script src="https://cdn.bootcdn.net/ajax/libs/twitter-bootstrap/3.4.1/js/bootstrap.min.js"></script>
    {% load static %}
</head>
<body>
<div class="container-fluid">
    <div class="row">
        <div class="col-md-8 col-md-offset-2">
            <h1 class="text-center">登录</h1>
            <div class="form-group">
                <label for="username">用户名</label>
                <input type="text" name="username" class="form-control" id="username">
            </div>
            <div class="form-group">
                <label for="password">密码</label>
                <input type="password" name="password" class="form-control"id="password">
            </div>
            <div class="form-group">
                <label for="">验证码</label>
                <div class="row">
                    <div class="col-md-6">
                        <input type="text" name="code" id="id_code" class="form-control">
                    </div>
                    <div class="col-md-6">
                        <img src="/get_code/" alt="" width="380" height="35" id="id_img">
                    </div>
                </div>
            </div>
            <input type="button" class="btn btn-success" value="登录"id="id_commit">
            <span style="color: red" id="id_error"></span>
        </div>
    </div>
</div>
</body>
<script>
    $('#id_img').click(function () {
        //1.获取标签之间的src
        let oldVal = $(this).attr('src')
        $(this).attr('src', oldVal += '?')
    });
    //点击登录按钮
    $('#id_commit').click(function () {
        $.ajax({
            url:'',
            type:'post',
            data:{
                'username':$('#username').val(),
                'password':$('#password').val(),
                'code':$('#id_code').val(),
                'csrfmiddlewaretoken':'{{ csrf_token}}',
            },
            success:function (args) {
                if(args.code==1000){
                    //跳转到首页
                    window.location.href = args.url
                }else {
                    //渲染错误提示
                    $('#id_error').text(args.msg)
                }
            }
        })
    })
</script>
</html>

# 更多操作

```



## 搭建bbs首页

```python
def home(request):
    return render(request, 'home.html', locals())

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.bootcdn.net/ajax/libs/twitter-bootstrap/3.4.1/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.bootcdn.net/ajax/libs/jquery/3.4.1/jquery.min.js"></script>
    <script src="https://cdn.bootcdn.net/ajax/libs/twitter-bootstrap/3.4.1/js/bootstrap.min.js"></script>

</head>
<body>
<nav class="navbar navbar-inverse">
    <div class="container-fluid">
        <!-- Brand and toggle get grouped for better mobile display -->
        <div class="navbar-header">
            <button type="button" class="navbar-toggle collapsed" data-toggle="collapse"
                    data-target="#bs-example-navbar-collapse-1" aria-expanded="false">
                <span class="sr-only">Toggle navigation</span>
                <span class="icon-bar"></span>
                <span class="icon-bar"></span>
                <span class="icon-bar"></span>
            </button>
            <a class="navbar-brand" href="#">图书管理系统</a>
        </div>

        <!-- Collect the nav links, forms, and other content for toggling -->
        <div class="collapse navbar-collapse" id="bs-example-navbar-collapse-1">
            <ul class="nav navbar-nav">
                <li class="active"><a href="#">文章 <span class="sr-only">(current)</span></a></li>
                <li><a href="#">博客</a></li>
                <li class="dropdown">
                    <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true"
                       aria-expanded="false">更多 <span class="caret"></span></a>
                    <ul class="dropdown-menu">
                        <li><a href="#">Action</a></li>
                        <li><a href="#">Another action</a></li>
                        <li><a href="#">Something else here</a></li>
                        <li role="separator" class="divider"></li>
                        <li><a href="#">Separated link</a></li>
                        <li role="separator" class="divider"></li>
                        <li><a href="#">One more separated link</a></li>
                    </ul>
                </li>
            </ul>
            <form class="navbar-form navbar-left">
                <div class="form-group">
                    <input type="text" class="form-control" placeholder="Search">
                </div>
                <button type="submit" class="btn btn-default">Submit</button>
            </form>
            <ul class="nav navbar-nav navbar-right">
                {% if request.user.is_authenticated %}
                    <li><a href="#">{{ request.user.username }}</a></li>
                    <li class="dropdown">
                        <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true"
                           aria-expanded="false">更多操作 <span class="caret"></span></a>
                        <ul class="dropdown-menu">
                            <li><a href="#" data-toggle="modal" data-target=".bs-example-modal-lg">修改密码</a></li>
                            <li><a href="#">修改头像</a></li>
                            <li><a href="#">后台管理</a></li>
                            <li role="separator" class="divider"></li>
                            <li><a href="{% url 'logout' %}">退出登录</a></li>
                        </ul>
                        <div class="modal fade bs-example-modal-lg" tabindex="-1" role="dialog"
                             aria-labelledby="myLargeModalLabel">
                            <div class="modal-dialog modal-lg" role="document">
                                <h1 class="text-center">修改密码</h1>
                                <div class="modal-content">
                                    <div class="row">
                                        <div class="col-md-8 col-md-offset-2">
                                            <div class="form-group">
                                                <br>
                                                <br>
                                                <label for="">用户名</label>
                                                <input type="text" disabled value="{{ request.user.username }}"
                                                       class="form-control">
                                            </div>
                                            <div class="form-group">
                                                <label for="">原密码</label>
                                                <input type="password" id="id_old_password" class="form-control">
                                            </div>
                                            <div class="form-group">
                                                <label for="">新密码</label>
                                                <input type="password" id="id_new_password" class="form-control">
                                            </div>
                                            <div class="form-group">
                                                <label for="">确认密码</label>
                                                <input type="password" id="id_confirm_password" class="form-control">
                                            </div>
                                            <div class="modal-footer">
                                                <button type="button" class="btn btn-primary" id="id_edit">修改</button>
                                                <button type="button" class="btn btn-default" data-dismiss="modal">
                                                    关闭
                                                </button>
                                                <span style="color: red;" id="password_error"></span>
                                            </div>
                                            <br>
                                            <br>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </li>
                {% else %}
                    <li><a href="{% url 'reg' %}">注册</a></li>
                    <li><a href="{% url 'login' %}">登录</a></li>
                {% endif %}
            </ul>
        </div><!-- /.navbar-collapse -->
    </div><!-- /.container-fluid -->
</nav>
<script>
    //修改密码绑定点击事件
    $('#id_edit').click(function () {
        $.ajax({
            url:'/set_password/',
            type:'post',
            data:{
                'old_password':$('#id_old_password').val(),
                'new_password':$('#id_new_password').val(),
                'confirm_password':$('#id_confirm_password').val(),
                'csrfmiddlewaretoken':'{{ csrf_token }}'
            },
            success:function (args) {
                if(args.code==1000){
                    window.location.reload()
                }else{
                    $('#password_error').text(args.msg)
                }
            }
        })
    })
</script>
</body>
</html>
```

## admin后台管理

```python
使用工具创建超级用户
admin 密码admin123
manage.py@BBS > createsuperuser
bash -cl "/usr/bin/python3.6 /home/jrsmith/py_tools/pycharm-professional-2019.2.6/pycharm-2019.2.6/helpers/pycharm/django_manage.py createsuperuser /home/jrsmith/桌面/Items/BBS"
Tracking file by folder pattern:  migrations
Username:  admin
Email address:  
Warning: Password input may be echoed.
Password:  admin123
Warning: Password input may be echoed.
Password (again):  admin123
Superuser created successfully.

Process finished with exit code 0


"""
django提供了一个可视化的界面 方便操作模型表
进行数据的增删改查
"""
http://127.0.0.1:8000/admin/
        登录到admin
        
"""
想使用admin后台管理操作模型表需要到应用下注册模型告诉admin你要操作哪些表 
到你的应用下注册你的模型表
"""
from django.contrib import admin
from app01 import models
# Register your models here.

# 注册模型表
admin.site.register(models.UserInfo)
admin.site.register(models.Blog)
admin.site.register(models.Category)
admin.site.register(models.Tag)
admin.site.register(models.Article)
admin.site.register(models.Article2Tag)
admin.site.register(models.UpAndDown)
admin.site.register(models.Comment)


# 关键点 http://127.0.0.1:8000/admin/app01/userinfo/
```

```python
# 数据
1.文章
# 数据绑定的时候一定要注意用户和个人站点不要忘记绑定(防止跨表查询查询不到)
2 标签
3 标签和文章
	(标签和人的文章最好一对一)
```



## 根据导航条根据用户是否登录展示不同内容

```python

```

首页文章展示

用户头像展示(media配置)

```python
"""
1.网址所用的静态文件默认放在 static文件夹下面 
2. 用户上传的静态文件应该单独的放在某个文件夹中
"""
media配置
# 配置用户上传的文件的存储位置
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # 文件名可以自定义
# 会自动创建多集目录

# 如何开始后端指定文件夹资源配置
from django.views.static import serve
from BBS import settings
  # 暴露后端文件指定文件资源
    url(r'^media/(?P<path>.*)', serve, {'document_root':settings.MEDIA_ROOT}),
```



## 图片防盗链

```python
"""
如何避免其他网站通过本网站的url访问本网站的资源

# 简单防盗链
通过查看当前请求是哪里来的
如果是本网站则访问通过
其他网站则是拒绝访问

请求头里面有一个专门记录请求是来自那个网站的参数
	Referer: http://127.0.0.1:8000/asdsadsa/
"""
# 如何避免 
1.修改请求头referer
2.通过爬虫技术把资源下载到本地，然后放到自己的服务器上

```



## 个人站点页面搭建

```python
# 每个站点的主题不一样的原因
<link rel="stylesheet" href="/media/css/{{ blog.site_theme }}">
```



## 侧边栏筛选功能

```python
## 	标签



## 	日期
from django.db.models.functions import TruncMonth
    data_list = models.Article.objects.filter(blog=blog).annotate(mouth=TruncMonth('create_time')).values(
        'mouth').annotate(count_num=Count('pk')).values_list('mouth', 'count_num')
    # <QuerySet [{'mouth': datetime.date(2021, 4, 1), 'count_num': 1}, {'mouth': datetime.date(2021, 5, 1),
    # 'count_num': 1}, {'mouth': datetime.date(2022, 5, 1), 'count_num': 1}, {'mouth': datetime.date(2021, 6, 1),
    # 'count_num': 1}]>
    print(data_list)

    
    
## 	分类
"""
https:www.xxxx.com/tom/tag/python				标签
https:www.xxxx.com/tom/category/1.html			分类
https:www.xxxx.com/tom/article/2020/04.html		日期
"""

```



## 侧边栏筛选功能

```python
def site(request, username, **kwargs):
    """
    :param request:
    :param username:
    :param kwargs: 这里需要判断是否有值 有值则需要对article_list 进行额外的筛选操作
    :return:
    """
    # 1.先校验当前用户名对应的站点是否存在
    # 2.用户不存在应该返回一个404页面
    user_obj = models.UserInfo.objects.filter(username=username).first()
    if not user_obj:
        return render(request, 'error.html')
    blog = user_obj.blog
    article_list = models.Article.objects.filter(blog=blog)  # 进一步筛选

    current_page = request.GET.get("page", 1)
    all_count = article_list.count()
    page_obj = Pagination(current_page=current_page, all_count=all_count, per_page_num=3)
    page_queryset = article_list[page_obj.start:page_obj.end]

    # 侧边栏的筛选
    if kwargs:
        # print(kwargs)  # {'condition': 'tag', 'param': '1'}
        condition = kwargs.get('condition')
        param = kwargs.get('param')
        # 判断用户到底想按照哪个条件筛选数据
        if condition == 'category':
            page_queryset = article_list.filter(category_id=param)
            print(page_queryset)
        elif condition == 'tag':
            page_queryset = article_list.filter(tags__id=param)
        else:
            year, month = param.split('-')  # 2020-11  [2020,11]
            page_queryset = article_list.filter(create_time__year=year, create_time__month=month)

    # 1.查询当前用户所有的分类及分类下的文章数
    category_list = models.Category.objects.filter(blog=blog).annotate(count_num=Count('article__pk')).values_list(
        'name', 'count_num', 'pk')
    # print(category_list)    # <QuerySet [('jim的分类一', 2), ('jim的分类二', 1), ('jim的分类三', 1)]>
    # 2.查询当前用户的所有标签及标签下的文章数
    tag_list = models.Tag.objects.filter(blog=blog).annotate(count_num=Count('article__pk')).values_list(
        'name', 'count_num', 'pk')
    # print(tag_list)
    # 按照年月统计所有文章
    data_list = models.Article.objects.filter(blog=blog).annotate(mouth=TruncMonth('create_time')).values(
        'mouth').annotate(count_num=Count('pk')).values_list('mouth', 'count_num')
    # <QuerySet [{'mouth': datetime.date(2021, 4, 1), 'count_num': 1}, {'mouth': datetime.date(2021, 5, 1),
    # 'count_num': 1}, {'mouth': datetime.date(2022, 5, 1), 'count_num': 1}, {'mouth': datetime.date(2021, 6, 1),
    # 'count_num': 1}]>
    print(data_list[0])
    return render(request, 'site.html', locals())
```

## 文章详情页

```python
# url设计
/username/article/1
# 先验证url是否会被其他url顶替掉
url(r'^(?P<username>\w+)/article/(?P<article_id>\d+)/', views.article_detail)

# 文章详情页和个人站点基本一致，所以用模板的继承
# 侧边栏的渲染需要传入数据才能进行渲染 并且侧边栏在很多页面都要使用
1.自己拷贝
2.将侧边栏作为 inclusion_tag
"""
1.在应用下创建一个必需为templatetags文件夹
2.在该文件夹内创建一个任意名称的py文件
3.在该py文件下书写固定的两行代码
	from django import template
	register = template.Library()
	# 下面就可以书写 
	# 自定义过滤器
	# 自定义标签
	# 自定义inclusion_tag
"""

# left_menu
<div class="panel panel-primary">
    <div class="panel-heading">
        <h3 class="panel-title">文章分类</h3>
    </div>
    <div class="panel-body">
        {% for category in category_list %}
            <p><a href="/{{ username }}/category/{{ category.2 }}">{{ category.0 }}({{ category.1 }})</a></p>
        {% endfor %}

    </div>
</div>
<div class="panel panel-danger">
    <div class="panel-heading">
        <h3 class="panel-title">文章标签</h3>
    </div>
    <div class="panel-body">
        {% for tag in tag_list %}
            <p><a href="/{{ username }}/tag/{{ tag.2 }}">{{ tag.0 }}({{ tag.1 }})</a></p>
        {% endfor %}
    </div>
</div>
<div class="panel panel-info">
    <div class="panel-heading">
        <h3 class="panel-title">日期归档</h3>
    </div>
    <div class="panel-body">
        {% for data in data_list %}
            <p><a href="/{{ username }}/archive/{{ data.0|date:'Y-m' }}">{{ data.0|date:'Y年m月' }}({{ data.1 }})</a></p>
        {% endfor %}
    </div>
</div>
#  mytags
<div class="panel panel-primary">
    <div class="panel-heading">
        <h3 class="panel-title">文章分类</h3>
    </div>
    <div class="panel-body">
        {% for category in category_list %}
            <p><a href="/{{ username }}/category/{{ category.2 }}">{{ category.0 }}({{ category.1 }})</a></p>
        {% endfor %}

    </div>
</div>
<div class="panel panel-danger">
    <div class="panel-heading">
        <h3 class="panel-title">文章标签</h3>
    </div>
    <div class="panel-body">
        {% for tag in tag_list %}
            <p><a href="/{{ username }}/tag/{{ tag.2 }}">{{ tag.0 }}({{ tag.1 }})</a></p>
        {% endfor %}
    </div>
</div>
<div class="panel panel-info">
    <div class="panel-heading">
        <h3 class="panel-title">日期归档</h3>
    </div>
    <div class="panel-body">
        {% for data in data_list %}
            <p><a href="/{{ username }}/archive/{{ data.0|date:'Y-m' }}">{{ data.0|date:'Y年m月' }}({{ data.1 }})</a></p>
        {% endfor %}
    </div>
</div>

# base_templates
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.bootcdn.net/ajax/libs/twitter-bootstrap/3.4.1/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.bootcdn.net/ajax/libs/jquery/3.4.1/jquery.min.js"></script>
    <script src="https://cdn.bootcdn.net/ajax/libs/twitter-bootstrap/3.4.1/js/bootstrap.min.js"></script>
    <link rel="stylesheet" href="/media/css/{{ blog.site_theme }}">
</head>
<body>
<nav class="navbar navbar-inverse">
    <div class="container-fluid">
        <!-- Brand and toggle get grouped for better mobile display -->
        <div class="navbar-header">
            <button type="button" class="navbar-toggle collapsed" data-toggle="collapse"
                    data-target="#bs-example-navbar-collapse-1" aria-expanded="false">
                <span class="sr-only">Toggle navigation</span>
                <span class="icon-bar"></span>
                <span class="icon-bar"></span>
                <span class="icon-bar"></span>
            </button>
            <a class="navbar-brand" href="#">{{ blog.site_title }}</a>
        </div>

        <!-- Collect the nav links, forms, and other content for toggling -->
        <div class="collapse navbar-collapse" id="bs-example-navbar-collapse-1">
            <ul class="nav navbar-nav">
                <li class="active"><a href="#">文章 <span class="sr-only">(current)</span></a></li>
                <li><a href="#">博客</a></li>
                <li class="dropdown">
                    <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true"
                       aria-expanded="false">更多 <span class="caret"></span></a>
                    <ul class="dropdown-menu">
                        <li><a href="#">Action</a></li>
                        <li><a href="#">Another action</a></li>
                        <li><a href="#">Something else here</a></li>
                        <li role="separator" class="divider"></li>
                        <li><a href="#">Separated link</a></li>
                        <li role="separator" class="divider"></li>
                        <li><a href="#">One more separated link</a></li>
                    </ul>
                </li>
            </ul>
            <form class="navbar-form navbar-left">
                <div class="form-group">
                    <input type="text" class="form-control" placeholder="输入内容或标题进行搜索">
                </div>
                <button type="submit" class="btn btn-default">搜索</button>
            </form>
            <ul class="nav navbar-nav navbar-right">
                {% if request.user.is_authenticated %}
                    <li><a href="#">{{ request.user.username }}</a></li>
                    <li class="dropdown">
                        <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true"
                           aria-expanded="false">更多操作 <span class="caret"></span></a>
                        <ul class="dropdown-menu">
                            <li><a href="#" data-toggle="modal" data-target=".bs-example-modal-lg">修改密码</a></li>
                            <li><a href="#">修改头像</a></li>
                            <li><a href="#">后台管理</a></li>
                            <li role="separator" class="divider"></li>
                            <li><a href="{% url 'logout' %}">退出登录</a></li>
                        </ul>
                        <div class="modal fade bs-example-modal-lg" tabindex="-1" role="dialog"
                             aria-labelledby="myLargeModalLabel">
                            <div class="modal-dialog modal-lg" role="document">
                                <h1 class="text-center">修改密码</h1>
                                <div class="modal-content">
                                    <div class="row">
                                        <div class="col-md-8 col-md-offset-2">
                                            <div class="form-group">
                                                <br>
                                                <br>
                                                <label for="">用户名</label>
                                                <input type="text" disabled value="{{ request.user.username }}"
                                                       class="form-control">
                                            </div>
                                            <div class="form-group">
                                                <label for="">原密码</label>
                                                <input type="password" id="id_old_password" class="form-control">
                                            </div>
                                            <div class="form-group">
                                                <label for="">新密码</label>
                                                <input type="password" id="id_new_password" class="form-control">
                                            </div>
                                            <div class="form-group">
                                                <label for="">确认密码</label>
                                                <input type="password" id="id_confirm_password" class="form-control">
                                            </div>
                                            <div class="modal-footer">
                                                <button type="button" class="btn btn-primary" id="id_edit">修改</button>
                                                <button type="button" class="btn btn-default" data-dismiss="modal">
                                                    关闭
                                                </button>
                                                <span style="color: red;" id="password_error"></span>
                                            </div>
                                            <br>
                                            <br>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </li>
                {% else %}
                    <li><a href="{% url 'reg' %}">注册</a></li>
                    <li><a href="{% url 'login' %}">登录</a></li>
                {% endif %}
            </ul>
        </div><!-- /.navbar-collapse -->
    </div><!-- /.container-fluid -->
</nav>
<div class="container-fluid">
    <div class="col-md-3">
        {% load mytags %}
        {% left_menu username %}
    </div>
    {% block content %}

    {% endblock %}

        <div class="text-center">
            {{ page_obj.page_html|safe }}
        </div>
    </div>
</div>
</body>
</html>s
```

## bug

```python
# 站点左上角的站点标题 在base.html中使用blog渲染的  在article_detail 也需要渲染  传值给locals()
    user_obj = models.UserInfo.objects.filter(username=username).first()
    blog = user_obj.blog
```



## 将侧边栏制作成inclusion_tag

```python
from django import template
from app01 import models
from django.db.models import Count
from django.db.models.functions import TruncMonth

register = template.Library()


# 自定义inclusion_tag
@register.inclusion_tag('left_menu.html')
def left_menu(username):
    user_obj = models.UserInfo.objects.filter(username=username).first()
    blog = user_obj.blog
    # 1.查询当前用户所有的分类及分类下的文章数
    category_list = models.Category.objects.filter(blog=blog).annotate(count_num=Count('article__pk')).values_list(
        'name', 'count_num', 'pk')
    # print(category_list)    # <QuerySet [('jim的分类一', 2), ('jim的分类二', 1), ('jim的分类三', 1)]>
    # 2.查询当前用户的所有标签及标签下的文章数
    tag_list = models.Tag.objects.filter(blog=blog).annotate(count_num=Count('article__pk')).values_list(
        'name', 'count_num', 'pk')
    # print(tag_list)
    # 按照年月统计所有文章
    data_list = models.Article.objects.filter(blog=blog).annotate(mouth=TruncMonth('create_time')).values(
        'mouth').annotate(count_num=Count('pk')).values_list('mouth', 'count_num')
    # <QuerySet [{'mouth': datetime.date(2021, 4, 1), 'count_num': 1}, {'mouth': datetime.date(2021, 5, 1),
    # 'count_num': 1}, {'mouth': datetime.date(2022, 5, 1), 'count_num': 1}, {'mouth': datetime.date(2021, 6, 1),
    # 'count_num': 1}]>
    # print(data_list[0])
    return locals()


```



## 点赞点踩样式

```python
1.拷贝前端点赞点踩样式图标
2.css样式拷贝
	2.1图片防盗链的问题，将图片下载到本地
    
3.如何判断点踩或点赞 
#  $(this).hasClass('diggit') 判断是true还是false
  //给类action绑定点击事件
        $('.action').click(function () {
            //指代当前位置点击的标签
            $(this).hasClass('diggit')
        })
        
# 点赞点踩的逻辑很多，则在后端单独开设一个视图函数
```

```python
$('.action').click(function () {
            //指代当前位置点击的标签
            alert($(this).hasClass('diggit'));
            let isUp = $(this).hasClass('diggit');
            {#$.ajax({#}
            {#    url: 'up_and_down',#}
            {#    type: 'post',#}
            {#    data: {#}
            {#        'article_id': '{{ article_obj.pk }}',#}
            {#        'is_up': isUp,#}
            {#        'csrfmiddlewaretoken': '{{ csrf_token }}'#}
            {#    },#}
            {#    success: function (args) {#}
            {#        alert(args)#}
            {#    }#}
            });
        {##}
        })

                def up_and_down(request):
    """
    1.校验用户是否登录
    2.判断当前文章是否是用户自己写的(不能给自己点赞点踩)
    3.当前用户是否已经给当前文章点过赞或踩
    4.操作数据库
    :param request:
    :return:
    """
    if request.is_ajax():
        back_dic = {'code': 1000, 'msg': ''}
        # 1.校验用户是否登录
        if request.user.is_authenticated():
            article_id = request.POST.get('article_id')
            is_up = request.POST.get('is_up')
            # print(is_up, type(is_up))  # true <class 'str'>
            is_up = json.loads(is_up)  # True <class 'bool'>   json数据需要转换一下
            print(is_up, type(is_up))
            # 2.判断当前文章是否是用户自己写的(不能给自己点赞点踩)
            # 根据文章id查文章对象 根据文章对象查询user 和request.user比对
            article_obj = models.Article.objects.filter(pk=article_id).first()
            if not article_obj.blog.userinfo == request.user:
                # 3.当前用户是否已经给当前文章点过赞或踩
                is_click = models.UpAndDown.objects.filter(user=request.user, article=article_obj)
                if not is_click:
                    #   4.操作数据库     同步操作普通字段
                    # 判断当前用户给那个文章点了赞或者踩 决定给那个用户+1
                    if is_up:
                        # 给点赞数+1
                        models.Article.objects.filter(pk=article_id).update(up_num=F('up_num') + 1)
                        back_dic['msg'] = '点赞成功'
                    else:
                        # 给点踩数+1
                        models.Article.objects.filter(pk=article_id).update(down_num=F('down_nun') + 1)
                        back_dic['msg'] = '点踩成功'
                        # 操作点赞点踩关系表
                    models.UpAndDown.objects.create(user=request.user, article=article_obj, is_up=is_up)
                else:
                    back_dic['code'] = 1003
                    back_dic['msg'] = '你已经点过了，请不要重复点击'
            else:
                back_dic['code'] = 1004
                back_dic['msg'] = '自己不能给自己点赞'
        else:
            back_dic['code'] = 1005
            back_dic['msg'] = '请先<a href="/login/">登录</a>'
    return JsonResponse(back_dic)
```



## 根评论子评论

```python
# 根评论渲染方式
1.dom临时渲染
2.页面刷新render渲染
# 子评论
  点击回复按钮
    评论框自动聚焦
    将回复按钮所在的用户姓名显示出来
    评论框内部自动换行

```

## 后台管理搭建

```python
所有文件夹内部都可以根据功能的细化 再细分成多个文件夹
 <div class="col-md-10">
            <div>

                <!-- Nav tabs -->
                <ul class="nav nav-tabs" role="tablist">
                    <li role="presentation" class="active"><a href="#home" aria-controls="home" role="tab"
                                                              data-toggle="tab">文章</a></li>
                    <li role="presentation"><a href="#profile" aria-controls="profile" role="tab"
                                               data-toggle="tab">随笔</a></li>
                    <li role="presentation"><a href="#messages" aria-controls="messages" role="tab"
                                               data-toggle="tab">草稿</a></li>
                    <li role="presentation"><a href="#settings" aria-controls="settings" role="tab"
                                               data-toggle="tab">设置</a></li>
                </ul>

                <!-- Tab panes -->
                <div class="tab-content">
                    <div role="tabpanel" class="tab-pane active" id="home">文章页面</div>
                    <div role="tabpanel" class="tab-pane" id="profile">随笔页面</div>
                    <div role="tabpanel" class="tab-pane" id="messages">草稿页面</div>
                    <div role="tabpanel" class="tab-pane" id="settings">设置页面</div>
                </div>
            </div>
        </div>
```

## 添加文章(富文本编辑器的使用)

```python
"""
kindeditor编辑器		看文档
CKEditor 经典
https://ckeditor.com/docs/ckeditor5/latest/examples/builds/classic-editor.html
"""
# 文章简介 不能直接截取 
# xss攻击 
针对支持用户书写html代码的网站
对于用户书写的script标签我们需要处理
处理思路：
	1.注释标签内部内容
    2.直接将script标签删除

    
# 如何解决
	bs4模块
    beautifulsoup模块
    专门用来处理html界面
```

## 编辑器上传图片 

```python
def upload_image(request):
    """
    //成功时
    {
            "error" : 0,
            "url" : "http://www.example.com/path/to/file.ext"
    }
    //失败时
    {
            "error" : 1,
            "message" : "错误信息"
    }
    :param request:
    :return:
    """
    back_dic = {'error': 0}
    # 用户上传的文件也算是静态资源 需要放在media中
    if request.method == 'POST':

        file_obj = request.FILES.get('imgFile')
        file_dir = os.path.join(settings.BASE_DIR, 'media', 'article_img')
        # 判断当前文件夹是否存在
        if not os.path.isdir(file_dir):
            os.mkdir(file_dir)
        # 拼接图片的完整路径
        file_path = os.path.join(file_dir, file_obj.name)
        with open(file_path, 'wb') as f:
            for line in file_obj:
                f.write(line)
        back_dic['url'] = '/media/article_img/%s' % file_obj.name
    return JsonResponse(back_dic)
```



## 修改头像

```python
@login_required
def set_avatar(request):
    if request.method == 'POST':
        file_obj = request.FILES.get('avatar')
        # models.UserInfo.objects.filter(pk=request.user.pk).update(avatar=file_obj)
        # 1.自己手动加avatar前缀
        # 2.换一种更新方法
        user_obj = request.user
        user_obj.avatar = file_obj
        user_obj.save()
        return redirect('/home/')
    blog = request.user.blog
    username = request.user.username
    return render(request, 'set_avatar.html', locals())

```














































