from crm import models
enabled_admins = {}


class BaseAdmin(object):
    list_display = []
    list_filter = []


class CustomerAdmin(BaseAdmin):
    list_display = ['qq', 'name', 'status', 'source', 'consult_course', 'date']
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
