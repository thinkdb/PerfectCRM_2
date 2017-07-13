from django import template
from django.utils.safestring import mark_safe
import time

register = template.Library()


@register.simple_tag
def render_app_name(admin_class):
    return admin_class.model._meta.verbose_name


@register.simple_tag
def get_query_sets(admin_class):
    return admin_class.model.objects.all()


@register.simple_tag
def build_table_row(obj, admin_class):
    row_ele = ""
    for column in admin_class.list_display:
        # c = models.Customer.objects.all()[0]
        # c._meta.get_field('date')
        # ---->  <django.db.models.fields.DateTimeField: date>


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
