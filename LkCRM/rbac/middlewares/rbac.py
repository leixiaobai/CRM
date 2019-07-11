#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: Xiaobai Lei
import re

from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import (
    redirect, reverse, HttpResponse
)

from rbac.models import Permission
# 白名单列表
WHITE_URL_LIST = [
    r'^/login/$',
    r'^/logout/$',
    r'^/register/$',
    r'^/favicon.ico$',
    r'^/admin/.*',
    r'^/get_vaildcode_img/$',
]


class PermissionMiddleware(MiddlewareMixin):
    """权限验证中间件"""

    def process_request(self, request):
        # 1.当前访问的url
        current_path = request.path_info

        # 2.白名单判断,如果在白名单的就直接放过去
        for path in WHITE_URL_LIST:
            if re.search(path, current_path):
                return None

        # 3.检验当前用户是否登录
        # user_id = request.session.get('user_id')
        if not request.user.is_authenticated:
            return redirect(reverse('login'))

        # 面包屑导航栏层级记录,默认首页为第一位,主要存储title(展示在页面用)和url(用户点击后可直接跳转到相应页面)
        request.breadcrumb_list = [
            {
                'title': '首页',
                'url': '/index/',
            }
        ]
        # 4.获取用户权限信息并进行校验
        permission_list = request.session.get('permission_list')
        for item in permission_list:
            # 由于url的是以正则形式存储,因此采用正则与当前访问的url进行完全匹配,如果符合则证明有权限
            if re.search('^{}$'.format(item['url']), current_path):
                # 将当前访问路径的所属菜单pk记录到show_id中,用户访问子权限时依旧会显示父权限(二级菜单)
                request.show_id = item['parent_id'] or item['id']
                # 将当前访问的父子信息记录到breadcrumb_list中(面包屑导航栏)
                # 如果是子权限的话,就根据父权限id查出父权限信息,将父权限和子权限都记录下来
                parent_obj = Permission.objects.filter(pk=item['parent_id']).first()
                if item['parent_id']:
                    request.breadcrumb_list.extend([
                        {
                            'title': parent_obj.title,
                            'url': parent_obj.url,
                        },
                        {
                            'title': item['title'],
                            'url': item['url'],
                        }])
                else:
                    # 排除首页,因为首页初始化就存在了
                    if item['title'] != '首页':
                        request.breadcrumb_list.append({
                            'title': item['title'],
                            'url': item['url'],
                        })
                return None
        else:
            return HttpResponse("无此权限")
