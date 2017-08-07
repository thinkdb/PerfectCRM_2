from django.shortcuts import render
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
    col_obj = king_admin.enabled_admins[app_name][table_name]

    # from crm import models
    # print(col_obj.model.objects, models.UserProfile)

    # 动态过滤数据
    object_list, filter_conditions, orderby_key, query_content = utils.table_filter(request, col_obj)
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

    page_num = col_obj.list_per_page    # 需要与 tags.render_page_ele 里面的 page_num 相等, 每页显示的行数, 默认为20行
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
                  {"col_obj": col_obj,
                   "contacts": contacts,
                   "filter_conditions": filter_conditions,
                   "orderby_key": orderby_key,
                   "query_content": query_content,
                   "app_name": app_name})


def table_obj_change(request, app_name, table_name, wid):
    """
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
            form_obj.save()
    else:
        # 实例化类对象
        form_obj = model_form_class(instance=recode_info)


    return render(request, 'king_admin/table_obj_change.html', {'form_obj': form_obj,
                                                                'app_name': app_name,
                                                                'admin_class': admin_class})
