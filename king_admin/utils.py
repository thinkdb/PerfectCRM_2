#!/bin/env python3
# -*- coding:utf8 -*-
__author__ = 'think'


def table_filter(request, admin_class):
    """
    同时过滤并返回结果
    admin_class: 获取的数据对象
    filter_conditions: 所有需要过滤的列信息
    """

    filter_conditions = {}
    count_num = 0
    orderby_key = None
    page_num = admin_class.list_per_page  # 每页显示的行数, 默认为20行
    pages = request.GET.get('page', None)
    if pages:
        count_num = page_num * int(pages)

    for k, v in request.GET.items():
        if k == 'page' or k == 'o':  # 每页关键字，不能让其他参与数据过滤
            continue
        if v != 'All':
            filter_conditions[k] = v
    # admin_class.model.objects.filter(**filter_conditions).all()[count_num: page_num]
    # 现在的分页是每次都要查所有的数据，需要改成 limit n, m 形式

    # 获取排序的信息
    if request.GET.get('o'):
        orderby_key = request.GET.get('o')
        object_list = admin_class.model.objects.filter(**filter_conditions).all().order_by(orderby_key)
    else:
        object_list = admin_class.model.objects.filter(**filter_conditions).all()
    return object_list, filter_conditions, orderby_key


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
