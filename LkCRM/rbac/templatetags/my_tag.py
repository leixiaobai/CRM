#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: Xiaobai Lei
import re

from django.template import Library


register = Library()


@register.inclusion_tag('rbac/menu.html')
def get_menu_displays(request):
    permission_menu_dict = request.session.get('permission_menu_dict')

    for menu in permission_menu_dict.values():
        for reg in menu['menu_children']:
            # if re.search("^{}$".format(reg['url']), request.path):
            if request.show_id == reg['id']:
                reg['class'] = 'active'
                menu['menu_ul'] = 'show'
                menu['class'] = 'menu-open'
    return {'permission_menu_dict': permission_menu_dict}


@register.filter
def url_is_permission(url, request):
    """判断当前按钮url是否在权限列表"""
    permission_url_names = request.session.get('permission_url_names')
    return url in permission_url_names


@register.simple_tag
def get_role_url(request, rid):
    params = request.GET.copy()
    params._mutable = True
    params['rid'] = rid
    return params.urlencode()
