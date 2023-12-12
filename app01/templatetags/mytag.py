from django import template
from app01 import models
from django.db.models import Count
from django.db.models.functions import TruncMonth

register = template.Library()

# 自定义inclusion_tag
@register.inclusion_tag('left_menu.html')
def left_menu(username):
    # 构造侧边栏需要的数据
    user_obj = models.UserInfo.objects.filter(username=username).first()
    blog = user_obj.blog
    # 1、查询当前用户下的所有的分类及分类下的文章数
    category_list = models.Category.objects.filter(blog=blog).annotate(count_num=Count('article__pk')).values(
        'name',
        'count_num',
        'pk')
    # 2、查询当前用户下的所有的标签及标签下的文章数
    tag_list = models.Tag.objects.filter(blog=blog).annotate(count_num=Count('article__pk')).values('name',
                                                                                                    'count_num',
                                                                                                    'pk')
    # 3、查询当前用户下的所有的日期及其下的文章数
    month_list = models.Article.objects.filter(blog=blog).annotate(month=TruncMonth('create_time')).values(
        'month').annotate(count_num=Count('month')).values('month', 'count_num').order_by('-month')
    return locals()
