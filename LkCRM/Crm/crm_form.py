#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: Xiaobai Lei
import re

from django import forms
from django.core.exceptions import ValidationError
from django.forms import (
    ModelForm, fields as fid, widgets as wid
)

from multiselectfield.forms.fields import MultiSelectFormField
from Crm.models import (
    UserInfo, Customer, ConsultRecord, ClassStudyRecord, StudentStudyRecord
)

from django.contrib import admin


class UserReg(forms.Form):
    """注册form表单验证"""
    username=forms.CharField(error_messages={'required':'用户名不能为空'},
                             widget=wid.TextInput(attrs={'placeholder':'用户名'}))
    password=forms.CharField(error_messages={'required':'密码不能为空'},
                             widget=wid.PasswordInput(attrs={'placeholder': '密码'}))
    repeat_password=forms.CharField(error_messages={'required':'确认密码不能为空'},
                             widget=wid.PasswordInput(attrs={'placeholder': '确认密码'}))
    email=forms.EmailField(error_messages={'required':'邮箱不能为空','invalid':'邮箱格式有误'},
                             widget=wid.EmailInput(attrs={'placeholder': '邮箱'}))
    telphone=forms.CharField(required=False,widget=wid.TextInput(attrs={'placeholder': '电话号码'}))

    def clean_username(self):
        """用户名验证"""
        clean_user = self.cleaned_data.get('username')
        re_user = re.search('^[a-zA-Z][a-zA-Z0-9_]{4,15}$', clean_user)     # 看用户名是否满足5-16位
        if re_user:
            sql_user = UserInfo.objects.filter(username=clean_user).first()     # 看数据库是否有该用户
            if not sql_user:
                return clean_user
            raise ValidationError("该用户名已被注册")
        raise ValidationError("字母开头，5-16位，只允许字母数字下划线")

    def clean_password(self):
        """密码验证"""
        clean_pwd= self.cleaned_data.get('password')
        re_password = re.search(r'^.*(?=.{8,16})(?=.*[0-9a-zA-Z])(?=.*[_!@#$%^&*?\(\)]).*$', clean_pwd)     # 密码的规则
        if re_password:
            return clean_pwd
        raise ValidationError("密码8-16位,必须包含字母、数字和特殊字符的组合")

    def clean_repeat_password(self):
        """确认密码验证"""
        clean_rep_pwd= self.cleaned_data.get('repeat_password')
        re_rep_password = re.search(r'^.*(?=.{8,16})(?=.*[0-9a-zA-Z])(?=.*[_!@#$%^&*?\(\)]).*$', clean_rep_pwd)     # 确认密码的规则
        if re_rep_password:
            return clean_rep_pwd
        raise ValidationError("密码8-16位,必须包含字母、数字和特殊字符的组合")

    def clean_email(self):
        """邮箱验证"""
        clean_emails = self.cleaned_data.get('email')
        re_emails = re.search(r'^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$', clean_emails)     # 邮箱的规则
        if re_emails:
            return clean_emails
        raise ValidationError("邮箱格式有误")

    def clean_telphone(self):
        """电话验证"""
        clean_tel = self.cleaned_data.get('telphone')
        # 用户输入了电话号码才校验,没输入不校验,因为该字段可选
        if clean_tel:
            re_tel = re.search(r'^(13[0-9]|14[5|7]|15[0-3|5-9]|18[0-3|5-9])\d{8}$', clean_tel)     # 电话的规则
            if re_tel:
                return clean_tel
            raise ValidationError("电话号码格式有误")
        return clean_tel

    def clean(self):
        """验证两次密码输入是否一致"""
        pwd = self.cleaned_data.get('password')
        rep_pwd = self.cleaned_data.get('repeat_password')
        if pwd and rep_pwd and pwd!=rep_pwd:
            self.add_error('repeat_password', ValidationError("两次输入的密码不一致"))        # 给错误名称并加入到errors中
        return self.cleaned_data
    UserInfo.objects.values()


class UserRegModelForm(ModelForm):
    """构建注册的modelform"""
    rep_password = fid.CharField(widget=wid.PasswordInput(attrs={'placeholder': '确认密码'}),
                                 error_messages={'required':'确认密码不能为空'})
    class Meta:
        model = UserInfo
        fields = ['username', 'password', 'rep_password', 'email', 'telphone']
        widgets = {
            'username': wid.TextInput(attrs={'placeholder': '用户名'}),
            'password': wid.PasswordInput(attrs={'placeholder': '密码'}),
            'email': wid.EmailInput(attrs={'placeholder': '邮箱'}),
            'telphone': wid.TextInput(attrs={'placeholder': '电话号码'}),
        }
        error_messages = {
            'username': {'required':'用户名不能为空'},
            'password': {'required':'密码不能为空'},
            'email': {'required':'邮箱不能为空','invalid':'邮箱格式有误'},
        }

    def __init__(self, *args , **kwargs):
        """统一处理多个字段"""
        super(UserRegModelForm, self).__init__(*args , **kwargs)
        self.fields['telphone'].required = False
        self.fields['email'].required = True
        # for filed in self.fields.values():
        #     filed.error_messages={'required': '该字段不能为空'}

    def clean_username(self):
        """用户名验证"""
        clean_user = self.cleaned_data.get('username')
        re_user = re.search('^[a-zA-Z][a-zA-Z0-9_]{4,15}$', clean_user)     # 看用户名是否满足5-16位
        if re_user:
            sql_user = UserInfo.objects.filter(username=clean_user).first()     # 看数据库是否有该用户
            if not sql_user:
                return clean_user
            raise ValidationError("该用户名已被注册")
        raise ValidationError("字母开头，5-16位，只允许字母数字下划线")

    def clean_password(self):
        """密码验证"""
        clean_pwd= self.cleaned_data.get('password')
        re_password = re.search(r'^.*(?=.{8,16})(?=.*[0-9a-zA-Z])(?=.*[_!@#$%^&*?\(\)]).*$', clean_pwd)     # 密码的规则
        if re_password:
            return clean_pwd
        raise ValidationError("密码8-16位,必须包含字母、数字和特殊字符的组合")

    def clean_rep_password(self):
        """确认密码验证"""
        clean_rep_pwd= self.cleaned_data.get('rep_password')
        re_rep_password = re.search(r'^.*(?=.{8,16})(?=.*[0-9a-zA-Z])(?=.*[_!@#$%^&*?\(\)]).*$', clean_rep_pwd)     # 确认密码的规则
        if re_rep_password:
            return clean_rep_pwd
        raise ValidationError("密码8-16位,必须包含字母、数字和特殊字符的组合")

    def clean_email(self):
        """邮箱验证"""
        clean_emails = self.cleaned_data.get('email')
        re_emails = re.search(r'^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$', clean_emails)     # 邮箱的规则
        if re_emails:
            return clean_emails
        raise ValidationError("邮箱格式有误")

    def clean_telphone(self):
        """电话验证"""
        clean_tel = self.cleaned_data.get('telphone')
        # 用户输入了电话号码才校验,没输入不校验,因为该字段可选
        if clean_tel:
            re_tel = re.search(r'^(13[0-9]|14[5|7]|15[0-3|5-9]|18[0-3|5-9])\d{8}$', clean_tel)     # 电话的规则
            if re_tel:
                return clean_tel
            raise ValidationError("电话号码格式有误")
        return clean_tel

    def clean(self):
        """验证两次密码输入是否一致"""
        pwd = self.cleaned_data.get('password')
        rep_pwd = self.cleaned_data.get('rep_password')
        if pwd and rep_pwd and pwd!=rep_pwd:
            self.add_error('rep_password', ValidationError("两次输入的密码不一致"))        # 给错误名称并加入到errors中
        return self.cleaned_data


class CustomerModelForm(forms.ModelForm):
    """客户的modelform"""
    class Meta:
        model = Customer
        fields = "__all__"
        error_messages = {
            'qq': {'required': 'qq名称必须填写'},
            'course': {'required': '咨询课程必须勾选'},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for filed in self.fields.values():
            if not isinstance(filed,MultiSelectFormField):
                filed.widget.attrs.update({'class':'form-control'})


class ConsultRecordModelForm(forms.ModelForm):
    """跟进记录的modelform"""
    class Meta:
        model = ConsultRecord
        # fields = "__all__"
        exclude = ["delete_status"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        customer_choisces = [(i.id, i) for i in self.instance.consultant.customers.all()]
        customer_choisces.insert(0, ('', '---------'))
        # 限制客户是当前销售的私户
        print(self.fields)
        self.fields['customer'].widget.choices = customer_choisces
        # 限制跟进人是当前的销售
        self.fields['consultant'].widget.choices = [(self.instance.consultant.id, self.instance.consultant)]
        for filed in self.fields.values():
            filed.error_messages = {'required': '该字段不能为空'}
            filed.widget.attrs.update({'class':'form-control'})


class ClassStudyRecordModelForm(forms.ModelForm):
    """班级学习记录的modelform"""
    class Meta:
        model = ClassStudyRecord
        fields = "__all__"
        # exclude = ["delete_status"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for filed in self.fields.values():
            filed.error_messages = {'required': '该字段不能为空'}
            filed.widget.attrs.update({'class':'form-control'})


class StudentStudyRecordModelFormSet(forms.ModelForm):
    """学生记录表的modelformset"""
    class Meta:
        model = StudentStudyRecord
        fields = ['score', 'homework_note']

        widgets = {
            'homework_note': wid.TextInput({'class': 'form-control'}),
            'score': wid.Select({'class': 'form-control'})
        }