#!/bin/env python3
# -*- coding:utf8 -*-
__author__ = 'think'
from django.db.models import Q


def table_filter(request, admin_class):
    """
    同时过滤并返回结果
    admin_class: 获取的数据对象
    filter_conditions: 所有需要过滤的列信息
    """

    filter_conditions = {}
    ignore_keys = ['o', 'page', '_query']
    orderby_key = None

    # 添加过滤条件，key 为标签的 name 属性值， 需要提前设置好
    for k, v in request.GET.items():
        if k in ignore_keys:  # 关键字，不能让其他参与数据过滤
            continue
        if v != 'All':
            filter_conditions[k] = v

    # 获取检索数据
    query_content = request.GET.get('_query', '')
    q = Q()
    if query_content:
        q.connector = 'OR'
        for item in admin_class.search_fields:
            q.children.append(('%s__contains' % item, query_content))

    # 获取排序的信息
    if request.GET.get('o'):
        orderby_key = request.GET.get('o')
        object_list = admin_class.model.objects.filter(**filter_conditions).filter(q).all().order_by(orderby_key)
    else:
        ordering_keys = admin_class.ordering
        if ordering_keys:
            ordering = ordering_keys
        else:
            ordering = ['-id']
        object_list = admin_class.model.objects.filter(**filter_conditions).filter(q).all().order_by(*ordering)
    return object_list, filter_conditions, orderby_key, query_content


def request_order_data(request, admin_class):
    """
    :param request: 请求内容
    :param admin_class: 对应的数据对象
    :return: 返回排序后的数据 和 排序键
    """
    orderby_key = None
    if request.GET.get('o'):
        orderby_key = request.GET.get('o')
        return admin_class.order_by(orderby_key), orderby_key
    else:
        return admin_class, orderby_key
