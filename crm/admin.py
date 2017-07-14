from django.contrib import admin
from crm import models
# Register your models here.


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'qq', 'name', 'source', 'consultant', 'content', 'status', 'date')
    list_filter = ('source', 'consultant', 'date')
    search_fields = ('qq', 'name')
    raw_id_fields = ('consult_course',)
    filter_horizontal = ('tags',)
    list_editable = ('status',)


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'name')


admin.site.register(models.Branch)
admin.site.register(models.Course)
admin.site.register(models.Customer, CustomerAdmin)
admin.site.register(models.ClassList)
admin.site.register(models.CourseRecord)
admin.site.register(models.CustomerFollowUp)
admin.site.register(models.StudyRecode)
admin.site.register(models.Enrollment)
admin.site.register(models.Payment)
admin.site.register(models.Role)
admin.site.register(models.Tag)
admin.site.register(models.UserProfile, UserProfileAdmin)
admin.site.register(models.Menu)


# django 的注册功能是把 表的model信息 与 自定义的类（用于显示列，过滤列等信息的类）进行一个关联功能
# 数据为一个字典形式
# {app_name: {table_name: 自定义的类}}
