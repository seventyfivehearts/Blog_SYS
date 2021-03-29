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
