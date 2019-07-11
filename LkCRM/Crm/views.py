import random, datetime

from django.shortcuts import (
    render, reverse, HttpResponse, redirect
)
from django.contrib import auth
from django.http import JsonResponse
from django.views import View
from django.db.models import Q, Count
from django.forms import modelformset_factory
from PIL import (
    Image, ImageDraw, ImageFont
)
from io import BytesIO

from Crm.models import (
    Customer, ConsultRecord, UserInfo, ClassStudyRecord, StudentStudyRecord
)
from Crm.utils import myfunction
from Crm.utils.mypagination import MyPagination
from Crm.crm_form import (
    UserRegModelForm, CustomerModelForm, ConsultRecordModelForm, UserReg, ClassStudyRecordModelForm, StudentStudyRecordModelFormSet
)
from rbac.services.initial_permission import initial_session
from rbac.models import User


class LoginView(View):
    """登录"""
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        next_url = request.GET.get('next', '/index/')
        res = {'code': '', 'user': '', 'error_msg': '', 'next_url': next_url}
        username = request.POST.get('username')
        password = request.POST.get('password')
        valid_code = request.POST.get('validcode')
        check_code = request.session.get('check_code')
        if valid_code.upper() == check_code.upper():
            # 验证码输入正确再去判断用户名和密码,运用了django提供的auth组件
            user_obj = auth.authenticate(username=username, password=password)
            if user_obj:
                res['code'] = 1000
                res['user_info'] = username
                # 保存登录状态,实际上就是保存了session_id,源码主要代码request.session[SESSION_KEY] = user._meta.pk.value_to_string(user)
                auth.login(request, user_obj)
                # 获取rbac中的user对象,这里是因为嵌入了rbac,所以CRM用户表和rbac用户表做了1对1关联,因为权限认证要用rbac的用户表
                n_user = user_obj.user
                # 初始化用户,也就是读取用户的权限
                initial_session(n_user, request)
            else:
                res['code'] = 1001
                res['error_msg'] = '用户名或密码错误!'
        else:
            res['code'] = 1002
            res['error_msg'] = '验证码错误!'
        # 以json格式返回,实际上就是响应头说明返回是json数据,和将字典序列化了(dumps)
        return JsonResponse(res)

def register(request):
    """基于form组件的注册页面"""
    if request.method == "POST":
        res = {'code':'','error_msg':''}
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        telphone = request.POST.get('telphone')
        user_form = UserReg(request.POST)
        if user_form.is_valid():
            res['code'] = 2000
            # 注册时在权限用户表和crm用户表都创建相同用户,初始化给与访客的权限
            user = User.objects.create(name=username,pwd=password)
            user.roles.add(4)
            UserInfo.objects.create_user(username=username,password=password,email=email,telphone=telphone, user=user)
        else:
            res['code'] = 2001
            res['error_msg'] = user_form.errors     # 把不符合的错误全部返回
        return JsonResponse(res)
    user_form = UserReg()
    return render(request,'register.html',{'user_form':user_form})


# def reg_modelform(request):
#     """modelform构建的注册页面"""
#     if request.method == "POST":
#         user_modelform = UserRegModelForm(request.POST)
#         if user_modelform.is_valid():
#             # modelform提供save方法可直接保存ok的数据
#             user_modelform.save()
#             return redirect(reverse('login'))
#         return render(request, 'reg_modelform.html', {'user_modelform': user_modelform})
#     user_modelform = UserRegModelForm()
#     return render(request, 'reg_modelform.html', {'user_modelform': user_modelform})


def get_vaildcode_img(request):
    """生成验证码"""
    img = Image.new('RGB', (180, 38), myfunction.get_random_color())   # 生成随机底色
    draw = ImageDraw.Draw(img)  # 以img进行画画
    font = ImageFont.truetype("static/font/gordon.ttf", 35)     # 设置字体
    check_code = ""
    # 获取四个随机字符
    for i in range(4):
        random_num = str(random.randint(0, 9))
        random_lowstr = chr(random.randint(ord('a'), ord('z')))
        random_upperstr = chr(random.randint(ord('A'), ord('Z')))
        random_char = random.choice([random_num, random_lowstr, random_upperstr])
        draw.text((20+i*30+10, 0), random_char, myfunction.get_random_color(), font=font)     # 在img上写字
        check_code += random_char
    print(check_code)
    # 将用户个人的验证码保存到session中
    request.session['check_code'] = check_code
    # 加噪点和线
    # width = 180
    # height = 38
    # # 加10条线
    # for i in range(10):
    #     x1 = random.randint(0, width)
    #     x2 = random.randint(0, width)
    #     y1 = random.randint(0, height)
    #     y2 = random.randint(0, height)
    #     draw.line((x1,y1,x2,y2), fill=myfunction.get_random_color())
    #
    # # 加10个点
    # for i in range(10):
    #     draw.point([random.randint(0, width), random.randint(0, height)], fill=myfunction.get_random_color())
    #     x = random.randint(0, width)
    #     y = random.randint(0, height)
    #     draw.arc((x, y ,x+4, y+4), 0 , 90, fill=myfunction.get_random_color())

    # 将图片保存到内存
    f = BytesIO()
    img.save(f, "png")
    data = f.getvalue()     # 从内存中读取
    return HttpResponse(data)


def logout(request):
    """注销"""
    auth.logout(request)
    return redirect(reverse('login'))


def index(request):
    """crm首页"""
    return render(request, 'crm/index.html')


class CustomersList(View):
    """客户列表"""
    def get(self, request):
        # 通过反向解析获取的路径对比当前请求路径,返回查询不同的数据
        if reverse('allcustomers_list') == request.path:
            customer_list = Customer.objects.all()
        elif reverse('customers_list') == request.path:
            customer_list = Customer.objects.filter(consultant__isnull=True)
        else:
            customer_list = Customer.objects.filter(consultant=request.user)

        # 搜索的字段和内容
        search_field = request.GET.get('field_select')
        search_content = request.GET.get('table_search')
        if search_content:
            # Q的扩展使用
            q = Q()
            if search_field == 'consultant':
                q.children.append((search_field + "__username__icontains", search_content))
            else:
                q.children.append((search_field + "__icontains", search_content))
            customer_list = customer_list.filter(q)

        # 分页的使用
        current_page_num = request.GET.get('page')
        pagination = MyPagination(current_page_num, customer_list.count(), request)
        customer_list = customer_list[pagination.start:pagination.end]

        # 返回当前path,记录当前的path,新增,编辑后返回原来页面
        path = request.path
        next = "?next=%s" % path

        return render(request, "crm/customer_manager/customer_list.html",
                      {'next': next, 'customer_list': customer_list, 'pagination': pagination,
                       'search_field': search_field, 'search_content': search_content})

    def post(self, request):
        select_action = request.POST.get('select_action')
        selected_pk_list = request.POST.getlist('selected_pk_list')
        if hasattr(self, select_action):
            # 通过反射实现
            func = getattr(self, select_action)
            queryset = Customer.objects.filter(pk__in=selected_pk_list)
            func(request, queryset)
        return self.get(request)

    def delete_selected(self, request, queryset):
        """删除选中的数据"""
        queryset.delete()

    def public_to_private(self, request, queryset):
        """公户转私户"""
        if queryset.filter(consultant__isnull=True):
            queryset.update(consultant=request.user)

    def private_to_public(self, request, queryset):
        """私户转公户"""
        queryset.update(consultant=None)


class CustomerOperate(View):
    """客户信息操作(新增和编辑)"""
    def get(self, request, edit_id=None):
        customer_obj = Customer.objects.filter(pk=edit_id).first()
        # 注意,虽然新增没有edit_id,但是编辑有,注意modelform有instance=customer_obj
        customer_form = CustomerModelForm(instance=customer_obj)
        return render(request, "crm/customer_manager/customer_operate.html", {'customer_form':customer_form, 'customer_obj':customer_obj})

    def post(self, request, edit_id=None):
        customer_obj = Customer.objects.filter(pk=edit_id).first()
        # 如果不写instance=customer_obj,那么又是新增一条记录了
        customer_form = CustomerModelForm(request.POST, instance=customer_obj)
        if customer_form.is_valid():
            customer_form.save()
            # 跳转回编辑或添加前的页面
            return redirect(request.GET.get('next'))
        else:
            return render(request, "crm/customer_manager/customer_operate.html", {'customer_form':customer_form, 'customer_obj':customer_obj})


class CustomerDelete(View):
    """客户删除"""
    def get(self, request, delete_id):
        Customer.objects.filter(pk=delete_id).delete()
        # 跳转回删除前的页面
        return redirect(request.GET.get('next'))


class ConsultRecordList(View):
    """跟进记录列表"""
    def get(self, request):
        # 如果指定客户跟进记录则需要获取具体客户的跟进记录数据
        customer_id = request.GET.get('customer_id')
        # 获取当前用户的跟进记录数据
        consult_record_list = ConsultRecord.objects.filter(consultant=request.user)
        if customer_id:
            consult_record_list = consult_record_list.filter(customer=customer_id)
        # 搜索的字段和内容
        search_field = request.GET.get('field_select')
        search_content = request.GET.get('table_search')
        if search_content:
            q = Q()
            if search_field == 'customer':
                q.connector = 'or'
                q.children.append((search_field + "__qq__contains", search_content))
                q.children.append((search_field + "__name__icontains", search_content))
            else:
                q.children.append((search_field + "__icontains", search_content))
            consult_record_list = consult_record_list.filter(q)

        # 分页
        current_page_num = request.GET.get('page')
        pagination = MyPagination(current_page_num, consult_record_list.count(), request)
        consult_record_list = consult_record_list[pagination.start:pagination.end]

        return render(request, "crm/customer_manager/consult_record_list.html", {'consult_record_list':consult_record_list})

    def post(self, request):
        print(request.POST)
        select_action = request.POST.get('select_action')
        selected_pk_list = request.POST.getlist('selected_pk_list')
        if hasattr(self, select_action):
            func = getattr(self, select_action)
            queryset = ConsultRecord.objects.filter(pk__in=selected_pk_list)
            func(request, queryset)
        return self.get(request)

    def delete_selected(self, request, queryset):
        """删除选中的数据"""
        queryset.delete()


class ConsultRecordOperate(View):
    """跟进记录操作(新增和编辑)"""
    def get(self, request, edit_id=None):
        consult_record_obj = ConsultRecord.objects.filter(pk=edit_id).first()  or ConsultRecord(consultant=request.user)
        consult_record_list = ConsultRecordModelForm(instance=consult_record_obj)
        return render(request, 'crm/customer_manager/consult_record_operate.html', {'consult_record_list': consult_record_list})

    def post(self, request, edit_id=None):
        consult_record_obj = ConsultRecord.objects.filter(pk=edit_id).first() or ConsultRecord(consultant=request.user)
        consult_record_list = ConsultRecordModelForm(request.POST, instance=consult_record_obj)
        if consult_record_list.is_valid():
            consult_record_list.save()
            return redirect(reverse('consult_record_list'))
        else:
            return render(request, 'crm/customer_manager/consult_record_operate.html', {'consult_record_list': consult_record_list})


class ConsultRecordDelete(View):
    """跟进记录删除"""
    def get(self, request, delete_id):
        ConsultRecord.objects.filter(pk=delete_id).delete()
        return redirect(reverse('consult_record_list'))


class ClassStudyRecordList(View):
    """班级学习记录列表"""
    def get(self, request):
        class_study_record_list = ClassStudyRecord.objects.all()
        # 搜索的字段和内容
        search_field = request.GET.get('field_select')
        search_content = request.GET.get('table_search')
        if search_content:
            q = Q()
            q.connector = "or"
            q.children.append((search_field + "__course__icontains", search_content))
            q.children.append((search_field + "__semester__icontains", search_content))
            q.children.append((search_field + "__campuses__name__icontains", search_content))
            class_study_record_list = class_study_record_list.filter(q)
        # 分页
        current_page_num = request.GET.get('page')
        pagination = MyPagination(current_page_num, class_study_record_list.count(), request)
        class_study_record_list = class_study_record_list[pagination.start:pagination.end]
        return render(request, "crm/class_manager/class_study_record_list.html", {'class_study_record_list': class_study_record_list,
                                                                    'pagination': pagination})

    def post(self, request):
        select_action = request.POST.get('select_action')
        selected_pk_list = request.POST.getlist('selected_pk_list')
        if hasattr(self, select_action):
            getattr(self, select_action)(request, selected_pk_list)
        return self.get(request)

    def init_student_study_record(self, request, selected_pk_list):
        """批量生成班级学生记录"""
        try:
            for i in selected_pk_list:
                class_study_record_obj = ClassStudyRecord.objects.filter(id=i).first()
                student_list = class_study_record_obj.class_obj.students.all()

                for student in student_list:
                    StudentStudyRecord.objects.create(student=student, classstudyrecord=class_study_record_obj)
        except Exception as e:
            pass


class ClassStudyRecordOperate(View):
    """班级学习记录操作(新增和编辑)"""
    def get(self, request, edit_id=None):
        class_study_record_obj = ClassStudyRecord.objects.filter(pk=edit_id).first()
        class_study_record_list = ClassStudyRecordModelForm(instance=class_study_record_obj)
        return render(request, 'crm/class_manager/class_study_record_operate.html', {'class_study_record_list': class_study_record_list})

    def post(self, request, edit_id=None):
        class_study_record_obj = ClassStudyRecord.objects.filter(pk=edit_id).first()
        class_study_record_list = ClassStudyRecordModelForm(request.POST, instance=class_study_record_obj)
        if class_study_record_list.is_valid():
            class_study_record_list.save()
            return redirect(reverse('class_study_record_list'))
        else:
            return render(request, 'crm/class_manager/class_study_record_operate.html', {'class_study_record_list': class_study_record_list})


class ClassStudyRecordDelete(View):
    """跟进记录删除"""
    def get(self, request, delete_id):
        ClassStudyRecord.objects.filter(pk=delete_id).delete()
        return redirect(reverse('class_study_record_list'))


class RecordScoreView(View):
    """为班级批量录入成绩"""
    def get(self, request, id):
        # 根据表模型和表约束创建modelformset类(批量操作使用modelformset)
        model_formset_cls = modelformset_factory(model=StudentStudyRecord, form=StudentStudyRecordModelFormSet, extra=0)
        # 根据班级记录的id找出所有这个班级的学生记录
        queryset = StudentStudyRecord.objects.filter(classstudyrecord=id)
        # 将数据给modelformset,实例化,前端循环formset就可以取出对应的数据
        formset = model_formset_cls(queryset=queryset)
        class_study_record_list = ClassStudyRecord.objects.filter(pk=id).first()
        # 获取当前班级的所有学生记录
        student_study_record_list = class_study_record_list.studentstudyrecord_set.all()
        return render(request, "crm/class_manager/record_score.html", locals())

    def post(self, request, id):
        model_formset_cls = modelformset_factory(model=StudentStudyRecord, form=StudentStudyRecordModelFormSet, extra=0)
        formset = model_formset_cls(request.POST)
        if formset.is_valid():
            formset.save()
        return self.get(request, id)


class CustomerQuantity(View):
    """客户成交量统计"""
    def get(self, request):
        # 获取前端需要展示的天数,默认是今天
        date = request.GET.get('date', 'today')
        # 以年月日表示今天
        now = datetime.datetime.now().date()
        # 时延,分别是1天,一周,和一个月
        delta1 = datetime.timedelta(days=1)
        delta2 = datetime.timedelta(weeks=1)
        delta3 = datetime.timedelta(days=30)
        # 通过字典嵌套列表再包含字典的形式保存数据
        condition = {'today': [{'deal_date': now}, {'customers__deal_date': now}],
                     'yesterday': [{'deal_date': now-delta1}, {'customers__deal_date': now-delta1}],
                     'week': [{'deal_date__gte': now - delta2, 'deal_date__lte': now},
                              {'customers__deal_date__gte': now - delta2, 'customers__deal_date__lte': now}],
                     'month': [{'deal_date__gte': now - delta3, 'deal_date__lte': now},
                              {'customers__deal_date__gte': now - delta3, 'customers__deal_date__lte': now}],
                     }
        # 根据条件查询出所有的客户
        customer_list = Customer.objects.filter(**(condition[date][0]))
        # 每个销售的成交量(根据时间不同进行筛选)
        customer_count = UserInfo.objects.filter(depart__name='销售部门').filter(**(condition[date][1])).annotate(
            c=Count('customers')).values_list('username', 'c')
        # 由于highchart接收的数据是[[]]这种格式,所以将querysey变成列表,发现[()]也可以
        customer_count = list(customer_count)
        return render(request, "crm/count_manager/customer_quantity.html", {'customer_count': customer_count,'customer_list': customer_list})
