from crm import models
"""
django 的注册功能是把 表的model信息 与 自定义的类（用于显示列，过滤列等信息的类）进行一个关联
数据为一个字典形式
enabled_admins = {app_name: {table_name: 自定义的类}}
"""
enabled_admins = {}


class BaseAdmin(object):
    list_display = []    # 需要显示的列名
    list_filters = []    # 参与过滤规则的列名
    list_per_page = 20   # 默认每页显示的行数
    search_fields = []   # 需要搜索的列名
    ordering = []        # 排序列, 正负号为排序顺序
    filter_horizontal = []  # 要显示多选框列
    radio_fields = []       # 单选列
    readonly_fields = []    # 只读列

    action = ['defaults_action']  # 默认的 action 动作

    def defaults_action(self, request, queryset):
        print(self, request, queryset)
        queryset.delete()


class CustomerAdmin(BaseAdmin):
    list_display = ['id', 'qq', 'name', 'status', 'source', 'consult_course', 'date']
    list_filters = ['status', 'source', 'consult_course', 'consultant', 'date']
    list_per_page = 2
    ordering = ['-id']
    search_fields = ['qq', 'name']
    filter_horizontal = ['tags']

    # model = models.Customer
    # 等于 admin_class.model = models_class
    # 外键数据需要添加 双下划线 consult_course__name


class UserProfileAdmin(BaseAdmin):
    list_display = ['user', 'name']
    search_fields = ['name']
    filter_horizontal = ['roles']


def register(models_class, admin_class=None):
    if models_class._meta.app_label not in enabled_admins:
        # 获取 app 名字
        enabled_admins[models_class._meta.app_label] = {}
        # enabled_admins['crm'] = {}
    if not admin_class:
        admin_class = BaseAdmin()
    admin_class.model = models_class
    # models.Customer, CustomerAdmin 使前面两个绑定在一起， 建立关系

    enabled_admins[models_class._meta.app_label][models_class._meta.model_name] = admin_class
    # enabled_admins['crm']['customer'] = CustomerAdmin

register(models.Customer, CustomerAdmin)
register(models.UserProfile, UserProfileAdmin)
# print(enabled_admins)
# print(enabled_admins['crm']['customer']().model)
