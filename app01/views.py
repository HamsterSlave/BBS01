import json
import os.path

from django.contrib import auth
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.shortcuts import render, HttpResponse, redirect
from app01.myforms import MyRegForm
from app01 import models
from django.contrib.auth.decorators import login_required


# Create your views here.


def register(request):
    form_obj = MyRegForm()
    if request.method == 'POST':
        # 校验数据是否合法
        form_obj = MyRegForm(request.POST)
        back_dic = {"code": 1000, 'msg': ''}
        # 判断数据是否合法
        if form_obj.is_valid():
            clean_data = form_obj.cleaned_data
            clean_data.pop('confirm_password')
            file_obj = request.FILES.get('avatar')
            if file_obj:
                clean_data['avatar'] = file_obj
            models.UserInfo.objects.create_user(**clean_data)
            back_dic['url'] = '/login/'
        else:
            back_dic['code'] = 2000
            back_dic['msg'] = form_obj.errors
        return JsonResponse(back_dic)
    return render(request, 'register.html', locals())


def login(request):
    if request.method == 'POST':
        back_dic = {'code': 1000, 'msg': ''}
        username = request.POST.get('username')
        password = request.POST.get('password')
        code = request.POST.get('code')
        # 验证验证码是否正确
        if request.session.get('code').upper() == code.upper():
            # 验证用户名和密码是否正确
            user_obj = auth.authenticate(request, username=username, password=password)
            if user_obj:
                # 保存用户状态
                auth.login(request, user_obj)
                back_dic['url'] = '/home/'
            else:
                back_dic['code'] = 2000
                back_dic['msg'] = '用户名或密码错误！'
        else:
            back_dic['code'] = 3000
            back_dic['msg'] = '验证码错误！'
        return JsonResponse(back_dic)
    return render(request, 'login.html')


'''
图片模块
install pillow
Image, 生成图片
ImageDraw, 在图片上涂画
ImageFont, 控制字体样式
'''
from PIL import Image, ImageDraw, ImageFont
import random
from io import BytesIO, StringIO


def get_random():
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)


def get_code(request):
    # with open(r'static/img/2.jpg','rb') as f:
    #     data = f.read()
    # return HttpResponse(data)
    # 利用pillow模块动态产生图片
    # img_obj = Image.new('RGB', (430, 35), get_random())
    # # 现将图片保存起来
    # with open(r'xxx.png', 'wb') as f:
    #     img_obj.save(f, 'png')
    # # 再将图片读取出来
    # with open('xxx.png', 'rb') as f:
    #     data = f.read()
    # return HttpResponse(data)
    """
    内存管理器模块
    BytesIO, 临时存储数据，返回的数据是二进制格式
    StringIO,临时存储数据，返回的数据是字符串格式
    """
    img_obj = Image.new('RGB', (430, 35), get_random())
    img_draw = ImageDraw.Draw(img_obj)
    img_font = ImageFont.truetype('static/font/111.ttf', 35)  # 字体样式和大小

    # 随机验证码 五位 数字 小写字母 大写字母
    code = ''
    for i in range(5):
        random_upper = chr(random.randint(65, 90))
        random_lower = chr(random.randint(97, 122))
        random_int = str(random.randint(0, 9))
        tmp = random.choice([random_upper, random_lower, random_int])
        # 一个一个写可以控制字体间隙
        img_draw.text((i * 60 + 60, 0), tmp, get_random(), img_font)
        code += tmp
    print(code)
    request.session['code'] = code
    io_obj = BytesIO()  # 生成一个内存管理器对象，可以看成是句柄
    img_obj.save(io_obj, 'png')
    return HttpResponse(io_obj.getvalue())


def home(request):
    article_queryset = models.Article.objects.all()
    user_obj = models.UserInfo.objects.filter(username=request.user)
    return render(request, 'home.html', locals())


@login_required
def set_password(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        back_dic = {'code': 1000, 'msg': ''}
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


@login_required
def logout(request):
    auth.logout(request)
    return redirect('/home/')


@login_required
def site(request, username, **kwargs):
    # 先校验当前用户名对应的个人站点是否存在
    user_obj = models.UserInfo.objects.filter(username=username).first()
    if not user_obj:
        return render(request, 'error.html')
    blog = user_obj.blog
    article_list = models.Article.objects.filter(blog=blog)
    if kwargs:
        condition = kwargs.get('condition')
        param = kwargs.get('param')
        if condition == 'category':
            article_list = article_list.filter(category_id=param)
        elif condition == 'tag':
            article_list = article_list.filter(tags__id=param)
        else:
            year, month = param.split('-')
            article_list = article_list.filter(create_time__year=year, create_time__month=month)
    # # 1、查询当前用户下的所有的分类及分类下的文章数
    # category_list = models.Category.objects.filter(blog=blog).annotate(count_num=Count('article__pk')).values('name',
    #                                                                                                           'count_num',
    #                                                                                                           'pk')
    # # 2、查询当前用户下的所有的标签及标签下的文章数
    # tag_list = models.Tag.objects.filter(blog=blog).annotate(count_num=Count('article__pk')).values('name',
    #                                                                                                 'count_num',
    #                                                                                                 'pk')
    # # 3、查询当前用户下的所有的日期及其下的文章数
    # month_list = models.Article.objects.filter(blog=blog).annotate(month=TruncMonth('create_time')).values(
    #     'month').annotate(count_num=Count('month')).values('month', 'count_num').order_by('-month')
    return render(request, 'site.html', locals())


def article_detail(request, username, article_id):
    user_obj = models.UserInfo.objects.filter(username=username).first()
    blog = user_obj.blog
    # 先获取文章对象
    article_obj = models.Article.objects.filter(pk=article_id, blog__userinfo__username=username).first()
    if not article_obj:
        return render(request, 'error.html')
    # 获取当前文章的所有评论内容
    comment_list = models.Comment.objects.filter(article_id=article_obj.id)
    return render(request, 'article_detail.html', locals())


from django.db.models import F


def up_or_down(request):
    """
    1.校验用户是否登录
    2.判断当前用户是否是当前用户自己写的（自己不能点自己的文章）
    3.当前用户是否给当前用户文章点过了
    4.操作数据库
    :param request:
    :return:
    """
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        back_dic = {'code': 1000, 'msg': ''}
        # 判断当前用户是否登录
        if request.user.is_authenticated:
            article_id = request.POST.get('article_id')
            is_up = request.POST.get('is_up')
            is_up = json.loads(is_up)  # 格式转换
            # 判断当前文章是否是当前用户写的
            article_obj = models.Article.objects.filter(pk=article_id).first()
            if not article_obj.blog.userinfo == request.user:
                # 校验当前用户是否已经点了
                is_click = models.UpandDown.objects.filter(user=request.user, article=article_obj)
                if not is_click:
                    # 操作数据库
                    if is_up:
                        # 点赞数加1
                        models.Article.objects.filter(pk=article_id).update(up_num=F('up_num') + 1)
                        back_dic['msg'] = '点赞成功'
                    else:
                        # 点踩数加1
                        models.Article.objects.filter(pk=article_id).update(down_num=F('down_num') + 1)
                        back_dic['msg'] = '点赞成功'
                    # 操作点赞点踩表
                    models.UpandDown.objects.create(user=request.user, article=article_obj, is_up=is_up)
                else:
                    back_dic['code'] = 1001
                    back_dic['msg'] = '你已经点过了，不能再次点击！'
            else:
                back_dic['code'] = 1002
                back_dic['msg'] = '自己无法给自己进行点赞点踩！'
        else:
            back_dic['code'] = 1003
            back_dic['msg'] = '请先<a href="/login/">登录</a>！'
    return JsonResponse(back_dic)


from django.db import transaction


def comment(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.method == 'POST':
            back_dic = {'code': 1000, 'msg': ''}
            if request.user.is_authenticated:
                article_id = request.POST.get('article_id')
                content = request.POST.get('content')
                parent_id = request.POST.get('parent_id')
                # 直接操作表 存储数据 两张表
                with transaction.atomic():
                    models.Article.objects.filter(pk=article_id).update(comment_num=F('comment_num') + 1)
                    models.Comment.objects.create(user=request.user, article_id=article_id, content=content,
                                                  parent_id=parent_id)
                back_dic['msg'] = '评论成功'
            else:
                back_dic['code'] = '1001'
                back_dic['msg'] = '用户未登录'
    return JsonResponse(back_dic)


from utils.mypage import Pagination


@login_required
def backend(request):
    username = request.user.username
    article_list = models.Article.objects.filter(blog=request.user.blog)
    page_obj = Pagination(current_page=request.GET.get('page', 1), all_count=article_list.count(), per_page_num=10)
    page_queryset = article_list[page_obj.start:page_obj.end]
    return render(request, 'backend/backend.html', locals())


from bs4 import BeautifulSoup


@login_required
def add_article(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get('category')
        tag_id_list = request.POST.get('tag')
        # 模块使用
        soup = BeautifulSoup(content, 'html.parser')
        # 获取所有标签
        tags = soup.find_all()
        for tag in tags:
            # print(tag.name)
            # 针对script标签直接删除
            if tag.name == 'script':
                tag.decomposed()
        # 文章简介，截取前150个字符
        # desc = content[0:150]
        desc = soup.text[0:150]
        # 写入数据库
        article_obj = models.Article.objects.create(
            title=title,
            content=str(soup),
            category_id=category_id,
            blog=request.user.blog,
            desc=desc
        )
        # 文章和文章标签是自己创建的,没法使用add set remove clear方法
        # 自己操作数据库表 一次性创建多条数据 批量插入bluk_create()
        article_obj_list = []
        for i in tag_id_list:
            article_obj_list.append(models.ArticleToTag(article=article_obj, tag_id=i))
        models.ArticleToTag.objects.bulk_create(article_obj_list)
        # 跳转后台展示页
        return redirect('/backend/')
    category_list = models.Category.objects.filter(blog=request.user.blog)
    tag_list = models.Tag.objects.filter(blog=request.user.blog)
    return render(request, 'backend/add_article.html', locals())


@login_required
def delete_article(request):
    if request.method == 'POST':
        back_dic = {'code': 1000, 'msg': ''}
        article_id = request.POST.get('id')
        try:
            res = models.Article.objects.filter(pk=article_id).delete()
            if res[0]:
                back_dic = {'code': 1000, 'msg': '删除成功!'}
            else:
                back_dic = {'code': 2000, 'msg': '删除失败!'}
        except:
            back_dic = {'code': 2000, 'msg': '删除失败!'}
    return JsonResponse(back_dic)


from BBS01 import settings
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.clickjacking import xframe_options_deny
from django.views.decorators.clickjacking import xframe_options_sameorigin


@xframe_options_exempt
def upload_image(request):
    if request.method == 'POST':
        back_dic = {'error': 0, }
        # 获取用户上传的图片对象
        file_obj = request.FILES.get('imgFile')
        # 手动拼接存储文件路径
        file_dir = os.path.join(settings.BASE_DIR, 'media', 'article_img')
        # 优化操作 文件夹不存在自动创建
        if not os.path.isdir(file_dir):
            os.mkdir(file_dir)
        # 文件完整路径
        file_path = os.path.join(file_dir, file_obj.name)
        with open(file_path, 'wb') as f:
            for line in file_obj:
                f.write(line)
        back_dic['url'] = '/media/article_img/%s' % file_obj.name
    return JsonResponse(back_dic)


from django.views.decorators.csrf import csrf_exempt, csrf_protect


@login_required
@csrf_exempt
def set_avatar(request):
    if request.method == 'POST':
        file_obj = request.FILES.get('avatar')
        if file_obj:
            # models.UserInfo.objects.filter(pk=request.user.pk).update(avatar=file_obj)
            # 对象更新可以自动加avatar前缀
            user_obj = request.user
            user_obj.avatar = file_obj
            user_obj.save()
    return redirect('/home/')


