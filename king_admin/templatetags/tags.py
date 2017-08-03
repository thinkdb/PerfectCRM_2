from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def render_app_name(admin_class):
    return admin_class.model._meta.verbose_name


@register.simple_tag
def get_query_sets(admin_class):
    return admin_class.model.objects.all()


@register.simple_tag
def build_table_row(obj, admin_class):
    """
    :param obj: 分页的数据对象
    :param admin_class: 获取的数据对象
    :return:
    """
    row_ele = ""
    for column in admin_class.list_display:
        # c = models.Customer.objects.all()[0]
        # c._meta.get_field('date')
        # ---->  <django.db.models.fields.DateTimeField: date>

        # 从分页的数据对象中获取具体的列信息
        field_obj = obj._meta.get_field(column)
        # print('----', field_obj.choices, column)
        if field_obj.choices:
            # 判断字段是否是 choices 字段
            column_data = getattr(obj, 'get_%s_display' % column)()
            # print('=======', column_data)
        else:
            column_data = getattr(obj, column)
            # print('column_data: ', column_data)

        if type(column_data).__name__ == 'datetime':
            # 转换时间列
            column_data = column_data.strftime("%Y-%m-%d %H:%M:%S")

        row_ele += "<td>%s</td>" % column_data

    return mark_safe(row_ele)


@register.simple_tag
def render_page_ele(page_counter, contacts, admin_class, filter_conditions, orderby_key):
    """
    :param page_counter: 循环的次数
    :param contacts: 分页的对象信息
    :param admin_class: 获取的数据对象
    :param filter_conditions: 分页时带入要过滤的参数
    :param orderby_key: 排序列
    :return:
    """
    ele = ''
    filters = ''
    orders = ''
    for k, v in filter_conditions.items():
        filters += "&%s=%s" % (k, v)
    if orderby_key:
        orders += "&o={order_key}".format(order_key=orderby_key)
    if abs(contacts.number - page_counter) <= admin_class.list_per_page:
        ele = '''<li><a href="?page=%s%s%s">%s</a></li>''' % (page_counter, filters, orders, page_counter)
    if contacts.number == page_counter:
        ele = '''<li class="active"><a href="?page=%s%s%s">%s</a></li>''' % (page_counter, filters, orders, page_counter)
    return mark_safe(ele)


@register.simple_tag
def render_page_previous_next(contacts, filter_conditions, orderby_key, query_content=''):
    filters = '?page=%s' % contacts
    if filter_conditions:
        for k, v in filter_conditions.items():
            filters += "&%s=%s" % (k, v)

    if orderby_key:
        filters += "&o={order_key}".format(order_key=orderby_key)

    if query_content:
        filters += "&_query={query}".format(query=query_content)

    return filters


@register.simple_tag
def render_filter_ele(condition, admin_class, filter_conditions):
    """
    :param condition: 需要过滤的列 列表
                      col_obj = king_admin.enabled_admins['crm']['customer']
                      col_obj.list_filters
                        --->  ['status', 'source', 'consult_course', 'consultant']
    :param admin_class: 获取的数据对象
    :param filter_conditions:  所有需要过滤的列信息
    :return:
    """
    select_ele = """<select class="form-control" name='%s'> <option>All</option>""" % condition
    field_obj = admin_class.model._meta.get_field(condition)
    # 获取列对象, 每个列都类型, 根据不同的列类型去做不同的事
    # 主要是 choices 、外键、多对多、一对多类型的数据需要二次处理

    # 处理 choices 类型的数据
    if field_obj.choices:
        selected = ""
        for choices_item in field_obj.choices:
            if str(choices_item[0]) == filter_conditions.get(condition):
                selected = "selected"
            select_ele += """<option %s value='%s'> %s </option>""" % (selected, choices_item[0], choices_item[1])
            selected = ""

    # 处理外键类型的数据
    if type(field_obj).__name__ == "ForeignKey":
        selected = ""
        for choices_item in field_obj.get_choices()[1:]:
            # 获取外键中的数据, 数据为元组类型, 第一个数据为 ------, 需要去除它, 所以使用切片功能
            if str(choices_item[0]) == filter_conditions.get(condition):
                selected = "selected"
            select_ele += """<option %s value='%s'> %s </option>""" % (selected, choices_item[0], choices_item[1])
            selected = ""

    select_ele += """</select>"""

    return mark_safe(select_ele)


@register.simple_tag
def build_table_header_orderby_column(column, orderby_key, filter_conditions):
    """
    单列排序
    :param column: 要显示的列名
    :param orderby_key: 要排序的列名
    :param filter_conditions: 过滤数据标签
    :return: 表格头部标签
    """

    filters = ''
    angle_str = ''
    for k, v in filter_conditions.items():
        filters += "&%s=%s" % (k, v)

    th_tag = """<th><a href="?o={order_key}{filters}">{column}</a>{angle}</th>"""
    if orderby_key and orderby_key.startswith('-'):
        ord_key = column
    else:
        ord_key = '-'+column
    if orderby_key and orderby_key.strip('-') == column:
        if orderby_key.startswith('-'):
            angle_str = '<i style=" padding: 3px 0 0 5px;color: #1f8cea;" class="fa fa-caret-down" aria-hidden="true"></i>'
        else:
            angle_str = '<i style=" padding: 3px 0 0 5px;color: #1f8cea;" class="fa fa-caret-up" aria-hidden="true"></i>'
    else:
        angle_str = ''
    return mark_safe(th_tag.format(order_key=ord_key, filters=filters, column=column, angle=angle_str))


@register.simple_tag
def render_page_top(filter_conditions, orderby_key):
    filters = '?page=1'
    if filter_conditions:
        for k, v in filter_conditions.items():
            filters += "&%s=%s" % (k, v)

    if orderby_key:
        filters += "&o={order_key}".format(order_key=orderby_key)

    return mark_safe(filters)


@register.simple_tag
def render_page_bottom(contacts, filter_conditions, orderby_key):
    filters = '?page=%s' % contacts.paginator.num_pages
    if filter_conditions:
        for k, v in filter_conditions.items():
            filters += "&%s=%s" % (k, v)

    if orderby_key:
        filters += "&o={order_key}".format(order_key=orderby_key)

    return mark_safe(filters)
