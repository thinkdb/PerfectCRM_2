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
    table_link = '<a href="/king_admin/{app}/{table}">{name}</a>'.format(app=app_name,
                                                                         table=col_obj.model._meta.object_name.lower(),
                                                                         name=col_obj.model._meta.verbose_name)
    return mark_safe("{app} / {table}".format(app=app_name.upper(), table=table_link))


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
def build_table_header_orderby_column(column, orderby_key, filter_conditions, query_content=''):
    """
    单列排序
    :param column: 要显示的列名
    :param orderby_key: 要排序的列名
    :param filter_conditions: 过滤数据标签
    :return: 表格头部标签
    """

    filters = ''
    angle_str = ''
    _query = ''
    for k, v in filter_conditions.items():
        filters += "&%s=%s" % (k, v)

    if query_content:
        _query += '&_query={content}'.format(content=query_content)

    th_tag = """<th><a href="?o={order_key}{filters}{query}">{column}</a>{angle}</th>"""
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
    return mark_safe(th_tag.format(order_key=ord_key, filters=filters, query=_query, column=column, angle=angle_str))


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
    if form_obj.instance.id:   # 更新数据
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

    else:  # 新增数据
        selected = []
    return selected


@register.simple_tag
def get_source_page(request):
    return request.path.replace('/del/', '/change/')


@register.simple_tag
def get_del_recode_info(recode_obj):
    return recode_obj.__str__().strip('<').strip('>')


@register.simple_tag
def get_select_del_recode_info(recode_obj):
    recode_list = []
    for recode in recode_obj:
        recode_list.append(recode.__str__().strip('<').strip('>'))
    return recode_list


@register.simple_tag
def print_admin_class(recode_obj):
    """
    获取对象及所有与其关联的数据
    :param recode_obj: 要操作的记录 对象
    :return:
    """
    objs = []
    try:
        len(recode_obj)
    # 这边添加到列表里面，是为删除多条记录时准备的，
        objs.append(recode_obj)
    except:
        objs.append([recode_obj])
    # print(recode_obj.model._meta.model_name)
    if objs:
        for obj in objs:
        # model_class = objs[0]._meta.model
        # model_name = objs[0]._meta.model_name
        # print(model_class, model_name)
            return mark_safe(recursive_related_objs_lookup(obj))


@register.simple_tag
def recursive_related_objs_lookup(objs):
    """
    生成 多对多, 多对一, 一对一的关联数据
    :param objs: 要操作的表对象
    :return:
    """
    ul_ele = "<ul>"
    for obj in objs:
        li_ele = """<li> {name}: {value} </li>""".format(name=obj._meta.verbose_name,
                                                         value=obj.__str__().strip('<>'))

        # obj = <Customer: 99685>
        # print(obj.__str__)
        #  ---> <bound method Customer.__str__ of <Customer: 99685>>

        # name 为m models 里面 Meta 定义的 verbose_name 的值
        # value 为 models 里面返回的名字, 就是下面的示例中的 self.xxxx
        # def __str__(self): return self.xxxx

        # 由于 return 返回值时,会自定义返回数据的类型，下面的 strip('<>') 就是把自定义返回值两边的 '<>' 删除
        # 这边要删除的内容需要根据 models 里面返回的数据格式匹配,不然无法删除多余的字符

        ul_ele += li_ele

        # 获取所有跟这个对象直接关联的 m2m 字段
        # print(obj._meta.local_many_to_many) / print(obj._meta.many_to_many)
        # ---> [<django.db.models.fields.related.ManyToManyField: tags>]

        for m2m_field in obj._meta.local_many_to_many:
            # m2m_field -->> crm.Customer.tags
            sub_ul_ele = "<ul>"

            # print(m2m_field, dir(obj))
            # m2m_field.name = tags

            m2m_field_obj = getattr(obj, m2m_field.name)
            # 等于  getattr(recode_obj, 'tags')
            # 等于执行了 models.Customer.objects.get(id=7).tags

            # print(m2m_field_obj, dir(m2m_field_obj))
            # ----> crm.Tag.None

            # models.Customer.tags.related_manager_cls.select_related
            for o in m2m_field_obj.select_related():
                # print(m2m_field_obj.select_related())
                # ----> <QuerySet [<Tag: aaa>, <Tag: bb>, <Tag: cccc>]> 重复多次

                # print(dir(m2m_field))
                li_ele = """<li> {name}: {value} </li>""".format(name=m2m_field.verbose_name,
                                                                 value=o.__str__().strip('<>'))
                # 展示形式为 多行
                # tags: aaa
                # tags: bb
                # tags: cccc

                # print(o.__str__())
                # aaa
                # bb
                # cccc

                sub_ul_ele += li_ele

            sub_ul_ele += "</ul>"
            ul_ele += sub_ul_ele

        # 多对一, 一对一
        # print(obj._meta.related_objects
        # 获取多对一对象, 返回结果为:
        #  --->  (<ManyToOneRel: crm.customerfollowup>, <ManyToOneRel: crm.enrollment>, <ManyToOneRel: crm.payment>)
        for related_obj in obj._meta.related_objects:

            # print(related_obj.__repr__())
            #    ----> <ManyToOneRel: crm.customerfollowup>

            if 'ManyToManyRel' in related_obj.__repr__():
                if hasattr(obj, related_obj.get_accessor_name()):

                    # 如果有,就获取
                    # Customer.customerfollowup_set.all()
                    accessor_obj = getattr(obj, related_obj.get_accessor_name())
                    # print(accessor_obj, dir(accessor_obj))
                    # ----> crm.CustomerFollowUp.None

                    # 判断 crm.CustomerFollowUp.None 里面有没有 select_related 方法, 获取所有关联的数据
                    if hasattr(accessor_obj, 'select_related'):
                        target_objs = accessor_obj.select_related()

                        # 等于 Customer.customerfollowup_set.all()
                        sub_ul_ele = "<ul>"
                        for o in target_objs:
                            li_ele = """<li> {name}: {value} </li>""".format(name=o._meta.verbose_name,
                                                                             value=o.__str__().strip('<>'))
                            sub_ul_ele += li_ele

                        sub_ul_ele += "</ul>"
                        ul_ele += sub_ul_ele

            # 获取所有以此表为主表的 外键 表， 也就是从表

            # print(related_obj.get_accessor_name())
            #    ----> customerfollowup_set
            # 反向查找时使用的对象
            # 判断 obj = Customer 里面 有没有 customerfollowup_set 等对象
            elif hasattr(obj, related_obj.get_accessor_name()):

                # 如果有,就获取
                # recode_obj.customerfollowup_set.all()
                accessor_obj = getattr(obj, related_obj.get_accessor_name())
                # print(accessor_obj, dir(accessor_obj))
                # ----> crm.CustomerFollowUp.None

                # 判断 crm.CustomerFollowUp.None 里面有没有 select_related 方法, 获取所有关联的数据
                if hasattr(accessor_obj, 'select_related'):
                    target_objs = accessor_obj.select_related()   # 查询所有联连的关联数据

                else:
                    target_objs = accessor_obj

                if len(target_objs) > 0:
                    # 递归操作
                    nodes = recursive_related_objs_lookup(target_objs)
                    ul_ele += nodes

    ul_ele += '</ul>'

    return ul_ele


@register.simple_tag
def build_action_ele(admin_class):
    option_ele = ""
    action_ele_verbose_name = admin_class.model._meta.verbose_name
    action_list = admin_class.action

    option_ele += "<option value='{id}'>{item}</option>".format(id='defaults_action',
                                                                item='Delete selected {table_name}'.format(
                                                                    table_name=action_ele_verbose_name))
    print(action_list)
    if action_list:
        for action in action_list:
            if hasattr(admin_class, action):
                display = admin_class.action_display[action]
                action_display = display.format(table_name=action_ele_verbose_name)
                option_ele += "<option value='{id}'>{item}</option>".format(id=action,
                                                                            item=action_display)
    return mark_safe(option_ele)
