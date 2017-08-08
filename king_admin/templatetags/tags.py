from django import template
from django.utils.safestring import mark_safe
from django.utils.timezone import datetime, timedelta
# 使用 django 系统时区的时间数据, 不能使用操作系统默认的时间, 无法处理 django 的时区问题

register = template.Library()


@register.simple_tag
def render_app_name(admin_class):
    return admin_class.model._meta.verbose_name


@register.simple_tag
def build_titile_ele(app_name, col_obj):
    return "{app} / {table}".format(app=app_name.upper(), table=col_obj.model._meta.verbose_name)


@register.simple_tag
def get_query_sets(admin_class):
    return admin_class.model.objects.all()


@register.simple_tag
def build_table_row(request, obj, admin_class):
    """
    :param request: 请求链接数据
    :param obj: 分页的数据对象
    :param admin_class: 获取的数据对象
    :return: 返回每列数据
    """
    row_ele = ""
    for index, column in enumerate(admin_class.list_display):
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

        # 为第一列添加一个 a 标签，用来编辑此行数据
        if index == 0:
            # 如果主键名不是　id， 这边会报错
            column_data = "<a href={request_path}{obj_id}/change>{data}</a>".format(request_path=request.path,
                                                                                    obj_id=obj.id,
                                                                                    data=column_data)

        row_ele += "<td>%s</td>" % column_data

    return mark_safe(row_ele)


@register.simple_tag
def render_page_ele(page_counter, contacts, admin_class, filter_conditions, orderby_key, query_content):
    """
    :param page_counter: 循环的次数
    :param contacts: 分页的对象信息
    :param admin_class: 获取的数据对象
    :param filter_conditions: 分页时带入要过滤的参数
    :param orderby_key: 排序列
    :param query_content: 查询列
    :return:
    """
    ele = ''
    filters = ''
    orders = ''
    _query = ''
    for k, v in filter_conditions.items():
        filters += "&%s=%s" % (k, v)
    if orderby_key:
        orders += "&o={order_key}".format(order_key=orderby_key)
    if query_content:
        _query += "&_query={query}".format(query=query_content)
    if abs(contacts.number - page_counter) <= admin_class.list_per_page:
        ele = '''<li><a href="?page=%s%s%s%s">%s</a></li>''' % (page_counter, filters, orders,  _query, page_counter)
    if contacts.number == page_counter:
        ele = '''<li class="active"><a href="?page=%s%s%s%s">%s</a></li>''' % (page_counter, filters, orders, _query, page_counter)
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
    select_ele = """<select class="form-control" name='{filter_field_name}'> <option>All</option>"""
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

    # 处理时间类型的数据
    if type(field_obj).__name__ in ("DateField", "DateTimeField"):
        date_eles = []
        today_ele = datetime.now().date()
        date_eles.append(['今天', today_ele])
        date_eles.append(['昨天', today_ele - timedelta(days=1)])
        date_eles.append(['近7天', today_ele - timedelta(days=7)])
        date_eles.append(['本月', today_ele.replace(day=1)])
        date_eles.append(['近30天', today_ele - timedelta(days=30)])
        date_eles.append(['近90天', today_ele - timedelta(days=90)])
        date_eles.append(['近半年', today_ele - timedelta(days=180)])
        date_eles.append(['本年', today_ele.replace(month=1, day=1)])
        date_eles.append(['近一年', today_ele - timedelta(days=365)])
        selected = ''

        # 设置 select 标签中的 name 属性值
        filter_field_name = '%s__gte' % condition
        for item in date_eles:
            if str(item[1]) == str(filter_conditions.get(filter_field_name)):
                selected = "selected"
            select_ele += """<option %s value='%s'> %s </option>""" % (selected, item[1], item[0])
            selected = ''

    else:
        filter_field_name = condition

    select_ele += """</select>"""

    select_ele = select_ele.format(filter_field_name=filter_field_name)
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
            angle_str = '<i style=" padding: 3px 0 0 5px;color: #1f8cea;" ' \
                        'class="fa fa-caret-down" aria-hidden="true"></i>'
        else:
            angle_str = '<i style=" padding: 3px 0 0 5px;color: #1f8cea;" ' \
                        'class="fa fa-caret-up" aria-hidden="true"></i>'
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


@register.simple_tag
def build_candidate_selected(admin_class, field, form_obj):
    """
     生成待选择的记录
    :param admin_class:
    :param field:
    :return:
    """
    # 表对象获取指定列的对象
    candidate_selected_obj = getattr(admin_class.model, field.name)

    # 通过数据行对象查找 多对多 的数据
    candidate_selected = candidate_selected_obj.rel.to.objects.all()

    # 已经选择的数据
    if form_obj.instance.id: # 更新数据
        selected_obj = getattr(form_obj.instance, field.name)
        selected = selected_obj.all()
    else: # 新数据
        return candidate_selected

    standby_obj_list = []
    # 已经选择的数据在待选择框不允许存在
    for obj in candidate_selected:
        if obj not in selected:
            standby_obj_list.append(obj)
    return standby_obj_list


@register.simple_tag
def build_selected(field, form_obj):
    """
    生成已经选择的数据
    :param admin_class: 表结构对象信息
    :param field: filter_horizontal 中的对象
    :return:
    """
    if form_obj.instance.id:  # 更新数据
        selected_obj = getattr(form_obj.instance, field.name)

        # selected_obj = getattr(admin_class.model.objects.last(), field.name)
        selected = selected_obj.all()

    else: # 新增数据
        selected = []
    return selected
