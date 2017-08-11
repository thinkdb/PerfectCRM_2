from django.shortcuts import render, redirect
from king_admin import king_admin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from king_admin import utils
from king_admin import forms

# Create your views here.


def index(request):
    return render(request, 'king_admin/table_index.html',
                  {'table_list': king_admin.enabled_admins})


def display_table_objs(request, app_name, table_name):
    """
    通用表格内容展示
    """
    # print(app_name, table_name)
    # import importlib
    # models_model = importlib.import_module('%s.models' % app_name)
    # model_obj = getattr(models_model, table_name)

    # 获取所有的列数据
    admin_class = king_admin.enabled_admins[app_name][table_name]

    # from crm import models
    # print(col_obj.model.objects, models.UserProfile)

    # action 动作
    if request.method == "POST":
        select_across = request.POST.get('select_across', None)
        post_flag = request.POST.get('_post', None)

        # 需要把 action 动作丢给 king_admin 来处理，包含返回的页面内容
        # filter_id = admin_class[0] + '__in'

        if select_across:
            action = request.POST.get('action', None)
            # filter_dic = {filter_id: select_across.split(',')}
            recode_obj = admin_class.model.objects.filter(id__in=select_across.split(','))
            if action:
                if hasattr(admin_class, action):
                    action_func = getattr(admin_class, action)
                    return action_func(admin_class, request, recode_obj)
        if post_flag:
            select_across = request.POST.get('_selected_action', None)
            action = request.POST.get('_action', None)
            if select_across:
                # filter_dic = {filter_id: select_across.split(',')}
                recode_obj = admin_class.model.objects.filter(id__in=select_across.split(','))
                if action:
                    if hasattr(admin_class, action):
                        action_func = getattr(admin_class, action)
                        return action_func(admin_class, request, recode_obj)

    # 动态过滤数据
    object_list, filter_conditions, orderby_key, query_content = utils.table_filter(request, admin_class)
    # 排序数据， 这边需要修改成使用统一的数据源，现在无法对过滤后的数据进行排序
    # object_list, orderby_key = utils.request_order_data(request, object_list)
    """
    object_list: 查询出来的数据
    filter_conditions: request.GET.items 的数据，动态查询的标签数据， 用于固定原来的选项
                       <option selected> 时使用的
    """



    """
    page
    """
    # 根据id来获取分页数据

    page_num = admin_class.list_per_page    # 需要与 tags.render_page_ele 里面的 page_num 相等, 每页显示的行数, 默认为20行
    page = request.GET.get('page')
    # id_range = int(page) * page_num
    # count_pages = col_obj.model.objects.count()
    # query_sets = col_obj.model.objects.filter(id__gte=id_range).all()[:page_num]

    # 获取过滤数据后, 进行分页, 如果没有过滤条件，则返回所有数据
    paginator = Paginator(object_list, page_num)
    # Show 1 contacts per page

    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        contacts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        contacts = paginator.page(paginator.num_pages)

    return render(request, 'king_admin/table_objs.html',
                  {"admin_class": admin_class,
                   "contacts": contacts,
                   "filter_conditions": filter_conditions,
                   "orderby_key": orderby_key,
                   "query_content": query_content,
                   "app_name": app_name})


def table_obj_del(request, app_name, table_name, wid):
    """
    删除表记录, 展示所有关联的数据
    :param request: 请求的链接信息
    :param app_name:
    :param table_name:
    :param wid: 记录的主键id值
    :return:
    """
    # 获取每个表的 model
    admin_class = king_admin.enabled_admins[app_name][table_name]

    # 根据数据主键，获取记录信息
    recode_obj = admin_class.model.objects.get(id=wid)
    # 等于 recode_obj = models.Customer.objects.get(id=7)

    # print(recode_obj, dir(recode_obj))
    # 99685 ['DoesNotExist', 'MultipleObjectsReturned', '__class__', '__delattr__', '__dict__', '__dir__', '__doc__',
    #  '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__le__', '__lt__',
    # '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__setstate__',
    # '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_check_column_name_clashes',
    # '_check_field_name_clashes', '_check_fields', '_check_id_field', '_check_index_together', '_check_local_fields',
    # '_check_long_column_names', '_check_m2m_through_same_relationship', '_check_managers', '_check_model',
    # '_check_model_name_db_lookup_clashes', '_check_ordering', '_check_swappable', '_check_unique_together',
    # '_do_insert', '_do_update', '_get_FIELD_display', '_get_next_or_previous_by_FIELD',
    #  '_get_next_or_previous_in_order', '_get_pk_val', '_get_unique_checks', '_meta', '_perform_date_checks',
    # '_perform_unique_checks', '_save_parents', '_save_table', '_set_pk_val', '_state', 'check', 'clean',
    #  'clean_fields', 'consult_course', 'consult_course_id', 'consultant', 'consultant_id', 'content',
    #  'customerfollowup_set', 'date', 'date_error_message', 'delete', 'enrollment_set', 'from_db', 'full_clean',
    #  'get_deferred_fields', 'get_next_by_date', 'get_previous_by_date', 'get_source_display', 'get_status_display',
    #  'id', 'memo', 'name', 'objects', 'payment_set', 'phone', 'pk', 'prepare_database_save', 'qq', 'qq_name',
    #  'referral_from', 'refresh_from_db', 'save', 'save_base', 'serializable_value', 'source', 'source_choice',
    #  'status', 'status_choice', 'tags', 'unique_error_message', 'validate_unique']

    if request.method == 'POST':
        recode_obj.delete()   # 删除数据, 跳转到所有记录页面
        return redirect('/king_admin/{app}/{table}'.format(app=app_name, table=table_name))

    return render(request, 'king_admin/table_obj_delete.html', {'admin_class': admin_class,
                                                                'app_name': app_name,
                                                                'recode_obj': recode_obj})


def table_obj_change(request, app_name, table_name, wid):
    """
    数据表修改记录
    :param request: 请求的链接信息
    :param app_name:
    :param table_name:
    :param wid: 记录的主键id值
    :return:
    """
    # 获取每个表的 model
    admin_class = king_admin.enabled_admins[app_name][table_name]

    # 动态创建 ModelForm 类对象
    model_form_class = forms.create_model_form(request, admin_class)

    # 根据数据主键，获取记录信息
    recode_info = admin_class.model.objects.get(id=wid)

    if request.method == 'POST':
        # 传入前端的数据,在传入数据库中的数据, 这时 form 会做更新操作, 如果只有前端数据, 只会新建一条记录
        form_obj = model_form_class(request.POST, instance=recode_info)
        if form_obj.is_valid:
            try:
                form_obj.save()
            except:
                pass
    else:
        # 实例化类对象
        form_obj = model_form_class(instance=recode_info)

    return render(request, 'king_admin/table_obj_change.html', {'form_obj': form_obj,
                                                                'app_name': app_name,
                                                                'admin_class': admin_class,
                                                                'table_name': table_name,
                                                                'recode_info': recode_info})


def table_obj_add(request, app_name, table_name):
    """
    数据表添加记录
    :param request: 请求的链接信息
    :param app_name:
    :param table_name:
    :return:
    """
    # 获取每个表的 model
    admin_class = king_admin.enabled_admins[app_name][table_name]

    # 动态创建 ModelForm 类对象
    model_form_class = forms.create_model_form(request, admin_class)

    if request.method == 'POST':
        # 传入前端的数据,在传入数据库中的数据, 这时 form 会做更新操作, 如果只有前端数据, 只会新建一条记录
        form_obj = model_form_class(request.POST)   # 新增数据
        if form_obj.is_valid:
            try:
                form_obj.save()
                return redirect(request.path.replace('/add/', '/'))    # 增加完后跳转到信息表页面
            except:
                pass
    else:
        # 实例化类对象
        form_obj = model_form_class()

    return render(request, 'king_admin/table_obj_add.html', {'form_obj': form_obj,
                                                             'app_name': app_name,
                                                             'admin_class': admin_class})
