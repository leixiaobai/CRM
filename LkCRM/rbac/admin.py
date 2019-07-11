from django.contrib import admin
from rbac.models import (
    Permission, Role, User, Menu
)


class PermissionConf(admin.ModelAdmin):
    """权限表admin中展示"""
    list_display = ['title', 'url', 'icon', 'menu', 'url_name']
    list_editable = ['url', 'icon', 'url_name']


class UserConf(admin.ModelAdmin):
    """用户表admin中展示"""
    list_display = ['name', 'pwd']


admin.site.register(Permission, PermissionConf)
admin.site.register(Role)
admin.site.register(User, UserConf)
admin.site.register(Menu)
