from django.forms import ModelForm
from django.forms import fields
from django.forms import models


def create_model_form(request, admin_class):
    """
    为每个表动态生成 ModelForm
    :param request: 请求的连接信息
    :param admin_class: 表的 model 信息
    :return: 返回表的 ModelForm 对象信息
    """

    def __new__(cls, *args, **kwargs):

        # cls 为每个表的 modelform 对象信息

        for field_name, field_obj in cls.base_fields.items():
            # print(dir(field_obj), field_obj)
            if field_obj.__class__ in (fields.TypedChoiceField, models.ModelChoiceField):
                # 定义选择框宽度
                field_obj.widget.attrs['style'] = 'width:80px;'
            else:
                field_obj.widget.attrs['style'] = 'width:300px;'
            field_obj.widget.attrs['class'] = 'form-control'

        return ModelForm.__new__(cls)

    class Meta:
        # 绑定具体的表， 也就是要操作的对象
        # 在king_admin 里面注册时 admin_class.model = models_class
        model = admin_class.model

        # 显示要操作的所有列，也可以是这个列表，显示指定的列
        fields = "__all__"

    attrs = {"Meta": Meta,
             "__new__": __new__}

    # 这里面是类的生成方法，__metaclass__
    _model_form_class = type("DynamicModelForm", (ModelForm, ), attrs)
    return _model_form_class
