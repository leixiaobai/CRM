#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: Xiaobai Lei
from rbac.models import Role


def initial_session(user_obj, request):
    """
    将当前登录人的信息记录到session中
    :param user_obj: 用户对象
    :param request:
    :return:
    """
    # 1.查询当前登录人的权限列表,取出相关的信息
    permissions = Role.objects.filter(user=user_obj).values('permissions__url',
                                                            'permissions__pk',
                                                            'permissions__title',
                                                            'permissions__icon',
                                                            'permissions__parent_id',
                                                            'permissions__url_name',
                                                            'permissions__menu__pk',
                                                            'permissions__menu__title',
                                                            'permissions__menu__weight',
                                                            'permissions__menu__icon').distinct()
    # 2.保存登录人的相关信息(权限列表,别名列表和权限菜单字典)
    """
    权限列表,以字典形式存储当前用户的每一个权限信息,数据格式如下:
    permission_list = [
        {'id': 1, 'url': '/custmer/list/', 'title': '客户列表', 'parent_id': None},
        {'id': 2, 'url': '/custmer/add/', 'title': '客户添加', 'parent_id': 1},
    ]
    原先简单设计只是列表保存当前用户的所有url,后面发现访问子权限(比如客户添加)时,依旧需要左侧客户列表展示,
    所以需要用到父权限(客户列表)的信息,而且为了更多扩展,所以采用了列表嵌套字典的形式保存了较多数据
    """
    # 权限列表,主要用于用户的权限校验
    permission_list = []
    # 别名列表,主要用于按钮级别的控制,比如客户添加的按钮
    permission_url_names = []
    """
    权限菜单字典,数据格式如下:
    permission_menu_dict = {
        '一级菜单id': {
            'menu_title': '信息管理',
            'menu_icon': '一级菜单图标',
            'menu_weight': '一级菜单的权重',
            'menu_children': [
                    {'id': 1, 'url': '/custmer/list/', 'title': '客户列表', 'parent_id': None},
                ]
        }
    }
    注意:menu_chidren只保存的是二级菜单(如客户列表),通过这个数据结构就可以很清晰的看到层级关系了,如果还有一级菜单
    的话,那么就需要在客户列表字典结构中再加入一个node_children:[{}],就是一个不断循环嵌套的过程,你懂的
    """
    # 权限菜单字典,主要用于左侧菜单的数据展示
    permission_menu_dict = {}

    # 循环获取上面提及的数据结构
    for item in permissions:
        permission_list.append({
            'url': item['permissions__url'],
            'id': item['permissions__pk'],
            'parent_id': item['permissions__parent_id'],
            'title': item['permissions__title'],
        })
        permission_url_names.append(item['permissions__url_name'])
        menu_id = item['permissions__menu__pk']
        # 只有二级菜单才被加入,也就是父权限(如客户列表)
        if menu_id:
            # 如果字典中已经存在了菜单id就直接在一级菜单的menu_chidren下追加,没有则先新建
            if menu_id not in permission_menu_dict:
                permission_menu_dict[menu_id] = {
                    'menu_title': item['permissions__menu__title'],
                    'menu_icon': item['permissions__menu__icon'],
                    'menu_weight': item['permissions__menu__weight'],
                    'menu_children': [
                        {
                          'title':  item['permissions__title'],
                          'url':  item['permissions__url'],
                          'icon':  item['permissions__icon'],
                          'id':  item['permissions__pk'],
                        },
                    ]
                }
            else:
                permission_menu_dict[menu_id]['menu_children'].append({
                    'title': item['permissions__title'],
                    'url': item['permissions__url'],
                    'icon': item['permissions__icon'],
                    'id':  item['permissions__pk'],
                })

    # 根据一级菜单权重进行重新排序
    permission_menu_dict_new = {}
    for i in sorted(permission_menu_dict, key=lambda x: permission_menu_dict[x]['menu_weight'], reverse=True):
        permission_menu_dict_new[i] = permission_menu_dict[i]
    # 将用户的权限列表和权限菜单列表注入session中
    request.session['permission_list'] = permission_list
    request.session['permission_url_names'] = permission_url_names
    request.session['permission_menu_dict'] = permission_menu_dict_new
