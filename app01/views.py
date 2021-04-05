from django.contrib import auth
from django.shortcuts import render, HttpResponse, redirect
from app01.myforms import MyRegForm
from app01 import models
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from utils.mypages import Pagination
from django.db.models import Count
from django.db.models.functions import TruncMonth


# Create your views here.


def register(request):
    back_dic = {'code': 1000, 'msg': ''}
    form_obj = MyRegForm()
    # 接受ajax传入的值
    if request.method == 'POST':
        # 校验数据是否合法
        form_obj = MyRegForm(request.POST)
        # # 判断数据是否合法
        if form_obj.is_valid():
            # print(form_obj.cleaned_data)
            clean_data = form_obj.cleaned_data  # 将校验通过的数据字典赋值给一个变量
            # 将字典中的确认密码删除
            clean_data.pop('confirm_password')
            # 用户头像
            """针对用户头像不能直接加到字典中去，需要判断是否传值 类似空指针"""
            file_obj = request.FILES.get('avatar')
            if file_obj:
                clean_data['avatar'] = file_obj
                # 直接操作数据库保存数据
            models.UserInfo.objects.create_user(**clean_data)
            # 注册成功跳转到登录界面
            back_dic['url'] = '/login/'
        else:
            back_dic['code'] = 2000
            back_dic['msg'] = form_obj.errors
        return JsonResponse(back_dic)
    return render(request, 'register.html', locals())


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


"""
图片相关的模块
pip3 install pillow
"""
from PIL import Image, ImageDraw, ImageFont
import random
from io import BytesIO, StringIO

"""
BytesIO 临时存储数据 返回的时候数据是二进制
StringIO  临时存储数据 返回的时候是字符串
"""
"""
Image   生成图片
ImageDraw   在图片上书写内容
ImageFont   控制字体样式
"""


# 产生随机颜色
def get_random():
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)


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
        img_draw.text((i * 60 + 60, -2), tmp, get_random(), img_font)
        code += tmp
    print(code)
    request.session['code'] = code
    io_obj = BytesIO()
    img_obj.save(io_obj, 'png')
    return HttpResponse(io_obj.getvalue())


# 首页相关
# 分页

def home(request):
    # 查询网站中所有的文章 可以使用分页
    article_queryset = models.Article.objects.all()
    article_list = models.Article.objects.all()
    current_page = request.GET.get("page", 1)
    all_count = article_list.count()
    page_obj = Pagination(current_page=current_page, all_count=all_count, per_page_num=3)
    page_queryset = article_list[page_obj.start:page_obj.end]
    return render(request, 'home.html', locals())


@login_required
def set_password(request):
    back_dic = {'code': 1000, 'msg': ''}
    if request.is_ajax():
        if request.method == 'POST':
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            is_right = request.user.check_password(old_password)
            if is_right:
                if new_password == confirm_password:
                    request.user.set_password(new_password)
                    request.user.save()
                    back_dic['msg'] = '修改成功'
                else:
                    back_dic['code'] = 1001
                    back_dic['msg'] = '两次密码不一致'
            else:
                back_dic['code'] = 1002
                back_dic['msg'] = '原密码错误'
        return JsonResponse(back_dic)
    return HttpResponse('ok')


@login_required
def logout(request):
    auth.logout(request)
    return redirect('/home/')


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
            # print(page_queryset)
        elif condition == 'tag':
            page_queryset = article_list.filter(tags__id=param)
        else:
            year, month = param.split('-')  # 2020-11  [2020,11]
            page_queryset = article_list.filter(create_time__year=year, create_time__month=month)

    # # 1.查询当前用户所有的分类及分类下的文章数
    # category_list = models.Category.objects.filter(blog=blog).annotate(count_num=Count('article__pk')).values_list(
    #     'name', 'count_num', 'pk')
    # # print(category_list)    # <QuerySet [('jim的分类一', 2), ('jim的分类二', 1), ('jim的分类三', 1)]>
    # # 2.查询当前用户的所有标签及标签下的文章数
    # tag_list = models.Tag.objects.filter(blog=blog).annotate(count_num=Count('article__pk')).values_list(
    #     'name', 'count_num', 'pk')
    # # print(tag_list)
    # # 按照年月统计所有文章
    # data_list = models.Article.objects.filter(blog=blog).annotate(mouth=TruncMonth('create_time')).values(
    #     'mouth').annotate(count_num=Count('pk')).values_list('mouth', 'count_num')
    # # <QuerySet [{'mouth': datetime.date(2021, 4, 1), 'count_num': 1}, {'mouth': datetime.date(2021, 5, 1),
    # # 'count_num': 1}, {'mouth': datetime.date(2022, 5, 1), 'count_num': 1}, {'mouth': datetime.date(2021, 6, 1),
    # # 'count_num': 1}]>
    # # print(data_list[0])
    return render(request, 'site.html', locals())


def article_detail(request,username,article_id):
    """
    应该需要校验username和article_id是否存在,但是我们这里先只完成正确的情况
    默认不会瞎搞
    :param request:
    :param username:
    :param article_id:
    :return:
    """
    user_obj = models.UserInfo.objects.filter(username=username).first()
    blog = user_obj.blog
    # 先获取文章对象
    article_obj = models.Article.objects.filter(pk=article_id,blog__userinfo__username=username).first()
    if not article_obj:
        return render(request,'error.html')
    # 获取当前 文章所有的评论内容
    comment_list = models.Comment.objects.filter(article=article_obj)
    return render(request,'article_detail.html',locals())



import json
from django.db.models import F


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


from django.db import transaction


def comment(request):
    # 自己也可以给自己的文章评论内容
    if request.is_ajax():
        back_dic = {'code': 1000, 'msg': ""}
        if request.method == 'POST':
            if request.user.is_authenticated():
                article_id = request.POST.get('article_id')
                content = request.POST.get("content")
                parent_id = request.POST.get('parent_id')
                # 直接操作评论表 存储数据      两张表
                with transaction.atomic():
                    models.Article.objects.filter(pk=article_id).update(comment_num=F('comment_num') + 1)
                    models.Comment.objects.create(user=request.user, article_id=article_id, content=content,
                                                  parent_id=parent_id)
                back_dic['msg'] = '评论成功'
            else:
                back_dic['code'] = 1001
                back_dic['msg'] = '用户未登陆'
            return JsonResponse(back_dic)
