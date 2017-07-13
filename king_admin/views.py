from django.shortcuts import render
from king_admin import king_admin
import importlib
# Create your views here.


def index(request):
    return render(request, 'king_admin/table_index.html',
                  {'table_list': king_admin.enabled_admins})


def display_table_objs(request, app_name, table_name):
    # print(app_name, table_name)
    # models_model = importlib.import_module('%s.models' % app_name)
    # model_obj = getattr(models_model, table_name)

    col_obj = king_admin.enabled_admins[app_name][table_name]

    # from crm import models
    # print(col_obj.model.objects, models.UserProfile)
    model_result = col_obj.model.objects.values_list(*col_obj.list_display)
    # print(model_result)
    for i in col_obj.model.objects.all():
        print(dir(i))
        print(dir(i.roles.source_field))


    return render(request, 'king_admin/table_objs.html',
                  {"col_obj": col_obj,
                   "model_result": model_result})
