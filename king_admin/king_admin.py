from crm import models
from django.core.validators import ValidationError
from django.shortcuts import render, redirect, HttpResponse
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
    readonly_table = False  # 只读表
    action = []  # 默认的 action 动作，

    # 控制在前端显示的内容， 最后一个{table_name}是必须的，显示要操作的表名
    # 想自定义 action 时，需要 设置 action, action_display 和 action 中定义的函数
    action_display = {
    }

    def defaults_action(self, request, queryset):
        """
        处理 action 的具体函数， 必须上传三个参数
        :param self: admin_class
        :param request: 请求的链接
        :param queryset: 要操作的对象集合
        :return:
        """

        app_name = self.model._meta.app_label
        select_across = request.POST.get('select_across', None)
        action = request.POST.get('action', None)

        if self.readonly_table:
            errors = {"readonly_table: ": "The table is readonly, can't be delete"}
        else:
            errors = {}

        if select_across:
            return render(request, 'king_admin/table_objs_delete.html', {'admin_class': self,
                                                                         'app_name': app_name,
                                                                         'recode_obj': queryset,
                                                                         'delete_id': select_across,
                                                                         'action': action,
                                                                         'errors': errors})
        else:
            select_across = request.POST.get('_selected_action', None)
            action = request.POST.get('_action', None)
            if select_across and action:
                if not self.readonly_table:
                    queryset.delete()

                return redirect(request.path)

    def coutom_validate(self):
        """
        自定义的数据校验, 相当于 django form 里面的 clean, 整体验证
        :param self: 前端传入的数据, 前端传入的 from_obj 对象
        :return:
        """
        # content = self.cleaned_data.get('content', '')
        # if len(content) < 20:
        #    return ValidationError(
        #        ValidationError('Invalid value.',
        #                        code='invalid',
        #                        params={'column': content}, )
        #    )

        pass

    """
    如果想要针对单独列进行验证，直接编写 clean_ + 列名的函数即可
    def clean_name(self):
        pass
    """


class CustomerAdmin(BaseAdmin):
    list_display = ['id', 'qq', 'name', 'status', 'source', 'consult_course', 'date']
    list_filters = ['status', 'source', 'consult_course', 'consultant', 'date']
    list_per_page = 2
    ordering = ['-id']
    search_fields = ['qq', 'name']
    filter_horizontal = ['tags']

    # 自定义 action 的内容
    # action = ['xxxx']
    # action_display = {'xxxx': '测试'}
    #
    # def xxxx(self, request, queryset):
    #     print('测试 action 项')
    #     return HttpResponse('测试 action 项')

    # model = models.Customer
    # 等于 admin_class.model = models_class
    # 外键数据需要添加 双下划线 consult_course__name

    readonly_fields = ['qq', 'source', 'tags']
    readonly_table = True

    # 针对具体的列进行验证
    # def clean_name(self):
    #     """
    #     :param: self 为 form_obj
    #     :return:
    #     """
    #     print(dir(self), self.cleaned_data.get('name'))


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
