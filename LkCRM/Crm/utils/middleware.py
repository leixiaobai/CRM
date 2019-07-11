#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: Xiaobai Lei
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect,reverse


class AuthLoginMiddleware(MiddlewareMixin):
    """登录认证中间件"""

    def process_request(self, request):

        # 不用认证的白名单
        isn_login = ['/admin/','/admin/login/', reverse('login'), reverse('get_vaildcode_img'), reverse('register')]
        if request.path in isn_login:
            return None

        if not request.user.is_authenticated:
            return redirect(reverse('login'))
