from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser


class UserInfo(AbstractUser):
    phone = models.BigIntegerField(verbose_name='手机号', null=True, blank=True)
    '''
    null=True 数据库该字段可以为空
    blank=True admin后台管理该字段可以为空
    '''
    # 头像
    avatar = models.FileField(upload_to='avatar/', default='avatar/default.jpg', verbose_name='头像')
    '''
    给avatar字段传文件对象，该文件会自动存储到avatar文件下，然后avatar字段只保存文件路径avatar/default.png
    '''
    create_time = models.DateField(auto_now_add=True)
    blog = models.OneToOneField(to='Blog', null=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = '用户表'

    def __str__(self):
        return self.username


class Blog(models.Model):
    site_name = models.CharField(verbose_name='站点名称', max_length=32)
    site_title = models.CharField(verbose_name='站点标题', max_length=32)
    site_theme = models.CharField(verbose_name='站点样式', max_length=64)  # 存css/js的路径

    class Meta:
        verbose_name_plural = '站点表'

    def __str__(self):
        return self.site_name


class Category(models.Model):
    name = models.CharField(verbose_name='文章分类', max_length=32)
    blog = models.ForeignKey(to='Blog', null=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = '文章分类表'

    def __str__(self):
        return self.name



class Tag(models.Model):
    name = models.CharField(verbose_name='文章标签', max_length=32)
    blog = models.ForeignKey(to='Blog', null=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = '文章标签表'

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField(verbose_name='文章标题', max_length=64)
    desc = models.CharField(verbose_name='文章简介', max_length=255)
    content = models.TextField(verbose_name='文章内容')
    create_time = models.DateField(auto_now_add=True)
    # 数据库字段设计优化
    up_num = models.BigIntegerField(default=0, verbose_name='点赞数')
    down_num = models.BigIntegerField(default=0, verbose_name='点踩数')
    comment_num = models.BigIntegerField(default=0, verbose_name='评论数')
    # 外键字段
    blog = models.ForeignKey(to='Blog', null=True, on_delete=models.CASCADE)
    category = models.ForeignKey(to='Category', null=True, on_delete=models.CASCADE)
    tags = models.ManyToManyField(to='Tag',
                                  through='ArticleToTag',
                                  through_fields=('article', 'tag'))

    class Meta:
        verbose_name_plural = '文章表'

    def __str__(self):
        return self.title


class ArticleToTag(models.Model):
    article = models.ForeignKey(to='Article', on_delete=models.CASCADE)
    tag = models.ForeignKey(to='Tag', on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = '文章和标签对应表'


class UpandDown(models.Model):
    user = models.ForeignKey(to='UserInfo', on_delete=models.CASCADE)
    article = models.ForeignKey(to='Article', on_delete=models.CASCADE)
    is_up = models.BooleanField()

    class Meta:
        verbose_name_plural = '点赞点踩表'


class Comment(models.Model):
    user = models.ForeignKey(to='UserInfo', on_delete=models.CASCADE)
    article = models.ForeignKey(to='Article', on_delete=models.CASCADE)
    content = models.CharField(max_length=255, verbose_name='评论内容')
    comment_time = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey(to='self', null=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = '评论表'
