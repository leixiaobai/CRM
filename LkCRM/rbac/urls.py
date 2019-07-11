from django.conf.urls import re_path

from rbac import views


app_name = 'rbac'
urlpatterns = [
    re_path(r'^role/list/$',views.role_list, name='role_list'),
    re_path(r'^role/add/$',views.role_operate, name='role_add'),
    re_path(r'^role/edit/(?P<edit_id>\d+)/$',views.role_operate, name='role_edit'),
    re_path(r'^role/del/(?P<del_id>\d+)/$',views.role_del, name='role_del'),

    re_path(r'^menu/list/$', views.menu_list, name='menu_list'),
    re_path(r'^menu/add/$', views.menu_operate, name='menu_add'),
    re_path(r'^menu/edit/(?P<edit_id>\d+)/$', views.menu_operate, name='menu_edit'),
    re_path(r'^menu/del/(?P<del_id>\d+)/$', views.menu_del, name='menu_del'),

    re_path(r'^permission/add/$', views.permission_operate, name='permission_add'),
    re_path(r'^permission/edit/(?P<edit_id>\d+)/$', views.permission_operate, name='permission_edit'),
    re_path(r'^permission/del/(?P<del_id>\d+)/$', views.permission_del, name='permission_del'),
    # 权限分配
    re_path(r'^distribute/permissions/$', views.distribute_permissions, name='distribute_permissions'),
]
