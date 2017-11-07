from django.db import models
from django.contrib.auth.models import AbstractUser


class Menu(models.Model):
    """
    菜单
    """
    title = models.CharField(verbose_name='菜单名称', max_length=32, unique=True)
    parent = models.ForeignKey(verbose_name='父级菜单', to="Menu", null=True, blank=True)
    # 定义菜单间的自引用关系
    # 权限url 在 菜单下；菜单可以有父级菜单；还要支持用户创建菜单，因此需要定义parent字段（parent_id）
    # blank=True 意味着在后台管理中填写可以为空，根菜单没有父级菜单

    def __str__(self):
        # 显示层级菜单
        title_list = [self.title]
        p = self.parent
        while p:
            title_list.insert(0, p.title)
            p = p.parent
        return '-'.join(title_list)


class Permission(models.Model):
    """
    权限
    """
    title = models.CharField(verbose_name='权限名称', max_length=32, unique=True)
    url = models.CharField(max_length=128, unique=True)
    menu = models.ForeignKey(verbose_name='所属菜单', to="Menu", null=True, blank=True)

    def __str__(self):
        # 显示带菜单前缀的权限
        return '{menu}---{permission}'.format(menu=self.menu, permission=self.title)


class Role(models.Model):
    """
    角色：绑定权限
    """
    title = models.CharField(verbose_name='角色名称', max_length=32, unique=True)

    permissions = models.ManyToManyField(verbose_name='权限', to="Permission")
    # 定义角色和权限的多对多关系

    def __str__(self):
        return self.title


class User(AbstractUser):
    """
    用户：划分角色
    """
    username = models.CharField(verbose_name='用户', max_length=32, unique=True)

    roles = models.ManyToManyField(verbose_name='角色', to="Role")
    # 定义用户和角色的多对多关系

    def __str__(self):
        return self.username



