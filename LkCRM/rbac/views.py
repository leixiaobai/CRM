from django.shortcuts import (
    render, redirect, reverse, HttpResponse
)
from django.db.models import Q

from rbac.models import (
    Role, Menu, Permission, User
)
from rbac.forms import (
    RoleModelForm, MenuModelForm, PermissionModelForm
)
from rbac.utils.mypagination import MyPagination


def role_list(request):
    """角色列表"""
    roles_list = Role.objects.all()
    # 分页
    current_page_num = request.GET.get('page')
    pagination = MyPagination(current_page_num, roles_list.count(), request)
    roles_list = roles_list[pagination.start:pagination.end]
    return render(request, 'rbac/role_list.html', {'roles_list': roles_list, 'pagination': pagination})


def role_operate(request, edit_id=None):
    """角色操作"""
    role_obj = Role.objects.filter(pk=edit_id).first()
    if request.method == "POST":
        role_form = RoleModelForm(request.POST, instance=role_obj)
        if role_form.is_valid():
            role_form.save()
            return redirect(reverse('rbac:role_list'))
        return render(request, 'rbac/role_operate.html', {'role_form': role_form})
    role_form = RoleModelForm(instance=role_obj)
    return render(request, 'rbac/role_operate.html', {'role_form': role_form, 'role_obj': role_obj})


def role_del(request, del_id):
    """删除角色"""
    Role.objects.filter(pk=del_id).delete()
    return redirect(reverse('rbac:role_list'))


def menu_list(request):
    """菜单权限列表"""
    # 获取所有的菜单
    menu_list = Menu.objects.all()
    # 菜单管理目前选择的菜单名称id
    mid = request.GET.get('mid')
    # 如果mid有值则通过二级菜单中菜单id是一级菜单的和二级菜单下子权限id属于一级菜单的全部找出来显示,没有则显示全部菜单
    if mid:
        permission_list = Permission.objects.filter(Q(parent__menu__id=mid) | Q(menu_id=mid))
    else:
        permission_list = Permission.objects.all()
    # 查询出权限表中的所有字段
    all_permission_list = permission_list.values('id', 'url', 'title', 'url_name',
                                                 'menu_id', 'parent_id', 'menu__title')
    # 把所有菜单以字典形式保存在字典中
    all_permission_dict = {}
    # 第一次for循环将二级菜单加入字典中
    for permission in all_permission_list:
        menu_id = permission.get('menu_id')
        # 有menu_id就证明是二级菜单,加入字典
        if menu_id:
            permission['children'] = []
            all_permission_dict[permission['id']] = permission
    # 第二次for循环将三级菜单(子权限)加入到二级菜单的children中
    for permission in all_permission_list:
        parent_id = permission.get('parent_id')
        if parent_id:
            all_permission_dict[parent_id]['children'].append(permission)
    return render(request, 'rbac/menu_list.html', {'menu_list': menu_list,
                                                   'all_permission_dict': all_permission_dict, 'mid': mid})


def menu_operate(request, edit_id=None):
    """菜单管理操作"""
    menu_obj = Menu.objects.filter(pk=edit_id).first()
    if request.method == "POST":
        form_obj = MenuModelForm(request.POST, instance=menu_obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(reverse('rbac:menu_list'))
        return render(request, 'rbac/menu_operate.html', {'form_obj': form_obj})
    form_obj = MenuModelForm(instance=menu_obj)
    return render(request, 'rbac/menu_operate.html', {'form_obj': form_obj, 'menu_obj': menu_obj})


def menu_del(request, del_id):
    """菜单管理删除"""
    Menu.objects.filter(pk=del_id).delete()
    return redirect(reverse('rbac:menu_list'))


def permission_operate(request, edit_id=None):
    """权限管理操作"""
    permission_obj = Permission.objects.filter(pk=edit_id).first()
    if request.method == "POST":
        form_obj = PermissionModelForm(request.POST, instance=permission_obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(reverse('rbac:menu_list'))
        return render(request, 'rbac/permission_operate.html', {'form_obj': form_obj})
    form_obj = PermissionModelForm(instance=permission_obj)
    return render(request, 'rbac/permission_operate.html', {'form_obj': form_obj, 'permission_obj': permission_obj})


def permission_del(request, del_id):
    """权限管理删除"""
    Permission.objects.filter(pk=del_id).delete()
    return redirect(reverse('rbac:menu_list'))


def distribute_permissions(request):
    """分配权限"""
    # uid是前端提交的用户id,rid是前端提交的角色id
    uid = request.GET.get('uid')
    rid = request.GET.get('rid')

    # 用户添加角色,由于有多个from表单所以给每个from表单一个postType
    if request.method == 'POST' and request.POST.get('postType') == 'role' and uid:
        user = User.objects.filter(id=uid).first()
        if not user:
            return HttpResponse('用户不存在')
        # 因为是多对多的关系,所以用set就可以直接更新数据了,记得set里面必须是可迭代对象,所以getlist
        user.roles.set(request.POST.getlist('roles'))
    # 角色添加权限
    if request.method == 'POST' and request.POST.get('postType') == 'permission' and rid:
        role = Role.objects.filter(id=rid).first()
        if not role:
            return HttpResponse('角色不存在')
        role.permissions.set(request.POST.getlist('permissions'))

    # 所有用户,界面用户展示
    user_list = User.objects.all()
    # 取得当前用户的所有角色
    user_has_roles = User.objects.filter(id=uid).values('id', 'roles')
    # 获取用户拥有的角色id,数据结构是{角色id: None},这种数据结构推荐,到时直接in就能判断了,效率高
    user_has_roles_dict = {item['roles']: None for item in user_has_roles}

    # 角色列表(所有角色),界面用户展示
    role_list = Role.objects.all()

    # 如过选中了角色,那么就根据角色id拿到所有的权限
    if rid:
        role_has_permissions = Role.objects.filter(id=rid).values('id', 'permissions')
    # 如果只选中了用户没有选择角色,那么就通过用户的角色去拿对应的所有权限
    elif uid and not rid:
        user = User.objects.filter(id=uid).first()
        if not user:
            return HttpResponse('用户不存在')
        role_has_permissions = user.roles.values('id', 'permissions')
    else:
        # 都没选中,就是初始化状态,界面不勾选任何权限菜单
        role_has_permissions = []

    # 获取角色拥有的权限id,数据结构是{权限id: None}
    role_has_permissions_dict = {item['permissions']: None for item in role_has_permissions}

    # 以列表形式存放所有的菜单信息
    all_menu_list = []

    # 查询出所有菜单
    menu_queryset = Menu.objects.values('id', 'title')
    # 以字典形式存放所有的菜单信息
    menu_dict = {}

    # 这个for循环的作用是将一级菜单信息分别放入了menu_dict字典和all_menu_list列表中
    for item in menu_queryset:
        item['children'] = []   # 存放二级菜单(父权限)
        menu_dict[item['id']] = item    # 注意这里是将item对象赋值给了item['id'],所以menu_dict和all_menu_list是一起变化的
        all_menu_list.append(item)

    """
    下面是这两个的数据结构,字典套字典,然后children字段子菜单就是列表,然后反复这样嵌套
    menu_dict = {'menu_id': {'id':1, 'title': 'xxx', 'children': [
                {'id', 'title', 'menu_id', 'children': [
                    {'id', 'title', 'parent_id'}
                ]},
                ]},
                None: {'id': None, 'title': '其他', 'children': [{'id', 'title', 'parent_id'}]}
                }
    all_menu_list = [
        {'id':1, 'title': 'xxx', 'children': [
        {'id', 'title', 'menu_id', 'children': [
            {'id', 'title', 'parent_id'}
        ]},
        ]},
        {'id': None, 'title': '其他', 'children': [{'id', 'title', 'parent_id'}]}
    ]
    """
    # 像首页这些不属于任何一级菜单,所以可以归属于other下面
    other = {'id': None, 'title': '其他', 'children': []}
    # 两个数据结构分别加入other
    all_menu_list.append(other)
    menu_dict[None] = other

    # 查询二级菜单的权限信息
    parent_permission = Permission.objects.filter(menu__isnull=False).values('id', 'title', 'menu_id')
    # 二级菜单信息字典
    parent_permission_dict = {}
    """
    parent_permission_dict = {父权限id: {'id', 'title', 'menu_id', 'children': [
        {'id', 'title', 'parent_id'}
    ]} }
    """

    for per in parent_permission:
        per['children'] = []    # 存放子权限
        nid = per['id']
        menu_id = per['menu_id']
        # 以二级菜单id为键,二级菜单信息为值加入到二级菜单字典中
        parent_permission_dict[nid] = per
        # 一级菜单字典将二级菜单加入到children下,注意一级菜单列表数据结构也会跟着增加(py内存使用导致)
        menu_dict[menu_id]['children'].append(per)

    # 类似上面的操作,将不是二级菜单的权限全部找出来,包括子权限和other
    node_permission = Permission.objects.filter(menu__isnull=True).values('id', 'title', 'parent_id')

    for per in node_permission:
        pid = per['parent_id']
        # 如果不是子权限,就将信息加入到other的children下
        if not pid:
            menu_dict[None]['children'].append(per)
            continue
        # 是子权限就加入到二级菜单的children下,因为menu_dict存放的是二级菜单的对象,所以此时menu_dict就有了各个层级的数据
        parent_permission_dict[pid]['children'].append(per)

    return render(request, 'rbac/distribute_permissions.html',
                  {
                      'user_list': user_list,
                      'role_list': role_list,
                      'user_has_roles_dict': user_has_roles_dict,
                      'role_has_permissions_dict': role_has_permissions_dict,
                      'all_menu_list': all_menu_list,
                      'uid': uid,
                      'rid': rid,
                  })
