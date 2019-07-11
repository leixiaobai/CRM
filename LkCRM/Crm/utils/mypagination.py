#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: Xiaobai Lei
import copy


class MyPagination(object):
    """自定义分页器"""

    def __init__(self, current_page_num, all_count, request, per_page_num=10, pager_show_count=9):
        """
        :param current_page_num:  当前用户选择的页数
        :param all_count:  数据库中数据的总数
        :param request:  用户提交的数据集合(主要是要拿用户请求的参数)
        :param per_page_num:  每页显示的条数
        :param pager_show_count:  最多显示的页码个数
        """

        try:
            # 如果用户输入的是非数字,则默认显示第一页
            current_page_num = int(current_page_num)
        except Exception as e:
            current_page_num = 1

        if current_page_num < 1:
            # 如果小于1页码无效,也返回第一页
            current_page_num = 1

        self.current_page_num = current_page_num
        self.all_count = all_count
        self.per_page_num = per_page_num
        self.url_params = copy.deepcopy(request.GET)
        print(self.url_params)

        # 计算得到总页数
        all_count_pager, tmp = divmod(all_count, per_page_num)
        if tmp:
            all_count_pager += 1
        self.all_count_pager = all_count_pager

        self.pager_show_count = pager_show_count
        self.pager_show_half_count = (self.pager_show_count - 1) // 2

    @property
    def start(self):
        """当前页数据切片的起点"""
        return (self.current_page_num - 1) * self.per_page_num

    @property
    def end(self):
        """当前页数据切片的终点"""
        return self.current_page_num * self.per_page_num

    def page_main(self):
        """根据用户自定义显示分页条"""
        page_num_list = []
        # 如果总页数小于最多显示的页码个数,就显示全部
        if self.all_count_pager <= self.pager_show_count:
            page_num_list = list(range(1, self.all_count_pager + 1))
        else:
            # 当前页面如果<=页面页码一半的时候,页面页码不发生变化
            if self.current_page_num  <= self.pager_show_half_count + 1:
                page_num_list = list(range(1, self.pager_show_count))
                page_num_list.append('...')
                page_num_list.append(self.all_count_pager)
            else:
                # 当页码翻到最后时
                if (self.current_page_num + self.pager_show_half_count) >= self.all_count_pager:
                    page_num_list.append(1)
                    page_num_list.append('...')
                    page_num_list.extend(list(range(self.all_count_pager - self.pager_show_count + 2 , self.all_count_pager + 1)))
                else:
                    page_num_list.append(1)
                    page_num_list.append('...')
                    page_num_list.extend(list(range(self.current_page_num - self.pager_show_half_count + 1, self.current_page_num + self.pager_show_half_count )))
                    page_num_list.append('...')
                    page_num_list.append(self.all_count_pager)

        # 存放分页的所有html标签
        page_html_list = []


        if self.current_page_num <= 1:
            prev_page = '<li class="disabled"><a href="javascript:void(0);">上一页</a></li>'
        else:
            self.url_params['page'] = self.current_page_num - 1
            prev_page = '<li><a href="?%s">上一页</a></li>' % (self.url_params.urlencode())
        page_html_list.append(prev_page)

        for i in page_num_list:
            if i == "...":
                temp = '<li class="disabled"><a href="javascript:void(0);">%s</a></li>' % (i)
                page_html_list.append(temp)
                continue
            self.url_params['page'] = i
            if i == self.current_page_num:
                temp = '<li class="active"><a href="?%s">%s</a></li>' % (self.url_params.urlencode(), i)
            else:
                temp = '<li><a href="?%s">%s</a></li>' % (self.url_params.urlencode(), i)
            page_html_list.append(temp)

        if self.current_page_num >= self.all_count_pager:
            next_page = '<li class="disabled"><a href="javascript:void(0);">下一页</a></li>'
        else:
            self.url_params['page'] = self.current_page_num + 1
            next_page = '<li><a href="?%s">下一页</a></li>' % (self.url_params.urlencode())
        page_html_list.append(next_page)


        return ''.join(page_html_list)