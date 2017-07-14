from crm import models
"""
django 的注册功能是把 表的model信息 与 自定义的类（用于显示列，过滤列等信息的类）进行一个关联功能
数据为一个字典形式
{app_name: {table_name: 自定义的类}}
"""
enabled_admins = {}


class BaseAdmin(object):
    list_display = []    # 需要显示的列信息
    list_filters = []    # 参与过滤规则的列信息
    list_per_page = 10   # 默认每页显示的行数


class CustomerAdmin(BaseAdmin):
    list_display = ['qq', 'name', 'status', 'source', 'consult_course', 'date']
    list_filters = ['status', 'source', 'consult_course', 'consultant']

    # model = models.Customer
    # 等于 admin_class.model = models_class


class UserProfileAdmin(BaseAdmin):
    list_display = ['user', 'name']


def register(models_class, admin_class=None):
    if models_class._meta.app_label not in enabled_admins:
        # 获取 app 名字
        enabled_admins[models_class._meta.app_label] = {}
        # enabled_admins['crm'] = {}

    admin_class.model = models_class
    # models.Customer, CustomerAdmin 使前面两个绑定在一起， 建立关系

    enabled_admins[models_class._meta.app_label][models_class._meta.model_name] = admin_class
    # enabled_admins['crm']['customer'] = CustomerAdmin

register(models.Customer, CustomerAdmin)
register(models.UserProfile, UserProfileAdmin)
# print(enabled_admins)
# print(enabled_admins['crm']['customer']().model)
