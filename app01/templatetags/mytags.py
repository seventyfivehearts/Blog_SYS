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

