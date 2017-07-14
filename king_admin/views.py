from django.shortcuts import render
from king_admin import king_admin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from king_admin import utils

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
    object_list, filter_conditions = utils.table_filter(request, col_obj)

    """
    page
    """
    # 根据id来获取分页数据

    page_num = col_obj.list_per_page    # 需要与 tags.render_page_ele 里面的 page_num 相等, 每页显示的行数, 默认为10行
    page = request.GET.get('page')
    # id_range = int(page) * page_num
    # count_pages = col_obj.model.objects.count()
    # query_sets = col_obj.model.objects.filter(id__gte=id_range).all()[:page_num]

    # 获取过滤数据后, 进行分页, 如果没有过滤条件，则返回所有数据
    query_sets = object_list
    paginator = Paginator(query_sets, page_num)
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
                   "filter_conditions": filter_conditions})
