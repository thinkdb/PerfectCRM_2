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

    for k, v in request.GET.items():
        if v != 'All':
            filter_conditions[k] = v


    return admin_class.model.objects.filter(**filter_conditions), filter_conditions