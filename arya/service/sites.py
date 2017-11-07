#!/usr/bin/env python
# -*- coding:utf-8 -*-
import copy
import json
from django.shortcuts import HttpResponse, render, redirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.http.request import QueryDict
from arya.utils.pagination import Page
from django.forms import ModelForm
from types import FunctionType
from django.db.models import ForeignKey, ManyToManyField
from django.db.models import Q


class FilterRow(object):
    """
    组合搜索项
    """
    def __init__(self, option, change_list, data_list, request):
        self.option = option
        self.data_list = data_list
        self.param_dict = copy.deepcopy(request.GET)
        self.param_dict._mutable = True
        self.change_list = change_list

    def __iter__(self):

        base_url = self.change_list.model_config.changelist_url
        tpl = "<a href='{url}' class='{active}'>{text}</a>"
        # 全部
        if self.option.name in self.param_dict:  # depart   ?depart=1 {'depart":1}
            pop_value = self.param_dict.pop(self.option.name)
            url = "{base_url}?{query_string}"\
                .format(base_url=base_url, query_string=self.param_dict.urlencode())
            val = tpl.format(url=url, active='', text='全部')
            self.param_dict.setlist(self.option.name, pop_value)
        else:
            url = "{base_url}?{query_string}"\
                .format(base_url=base_url, query_string=self.param_dict.urlencode())
            val = tpl.format(url=url, active='active', text='全部')

        # self.param_dict

        yield mark_safe("<div class='whole'>")
        yield mark_safe(val)
        yield mark_safe("</div>")

        yield mark_safe("<div class='others'>")
        for obj in self.data_list:  # for obj in depart.query_set

            param_dict = copy.deepcopy(self.param_dict)

            # url上要传递的值
            pk = self.option.val_func_name(obj) if self.option.val_func_name else obj.pk
            pk = str(pk)

            # a标签上显示的内容
            text = self.option.text_func_name(obj) if self.option.text_func_name else str(obj)

            exist = False
            if pk in param_dict.getlist(self.option.name):
                exist = True

            if self.option.is_multi:
                if exist:
                    values = param_dict.getlist(self.option.name)
                    values.remove(pk)
                    param_dict.setlist(self.option.name,values)
                else:
                    param_dict.appendlist(self.option.name, pk)
            else:
                param_dict[self.option.name] = pk

            url = "{base_url}?{query_string}"\
                .format(base_url=base_url, query_string=param_dict.urlencode())
            val = tpl.format(url=url, active='active' if exist else '', text=text)
            yield mark_safe(val)
        yield mark_safe("</div>")


class FilterOption(object):
    def __init__(self, field_or_func, is_multi=False, text_func_name=None, val_func_name=None, condition=None):
        """
        :param field: 字段名称或函数
        :param is_multi: 是否支持多选
        :param text_func_name: a标签上显示的内容， 默认str(obj)
        :param val_func_name:  url上要传递的值，默认 obj.pk
        :param condition: 显示过滤标签时，通过这个参数加以限定（默认是显示所有），值是Q对象
        
        """
        self.field_or_func = field_or_func
        self.is_multi = is_multi
        self.text_func_name = text_func_name
        self.val_func_name = val_func_name
        self.condition = condition

    @property
    def is_func(self):
        if isinstance(self.field_or_func, FunctionType):
            return True

    @property
    def name(self):
        if self.is_func:
            return self.field_or_func.__name__
        else:
            return self.field_or_func

    def get_condition(self):
        if self.condition:
            return self.condition
        condition = Q()
        return condition
        # 如果不存在，返回空的Q对象；否则ChangList中的gen_list_filter函数filter接收None会报错。


class ChangeList(object):
    def __init__(self, model_config, result_list):
        self.model_config = model_config

        self.show_add_btn = model_config.get_show_add_btn()
        self.list_display = model_config.get_show_list_display()
        self.actions = model_config.get_actions()
        self.list_filter = model_config.get_list_filter()
        self.list_search = model_config.get_list_search()

        self.result_list = result_list
        all_count = result_list.count()
        query_params = copy.copy(model_config.request.GET) # 根据url生成页码要用
        query_params._mutable = True

        self.pager = Page(model_config.request.GET.get('page'), all_count, base_url=model_config.changelist_url,
                          query_params=query_params)
        self.result_list = result_list[self.pager.start:self.pager.end]

    def add_html(self):
        """
        添加按钮
        :return: 
        """
        add_html = mark_safe('<a class="btn btn-primary" href="%s">添加</a>' % (self.model_config.add_url_params,))
        return add_html

    def gen_list_filter(self):

        for option in self.model_config.list_filter:
            # option是FilterOption对象
            if option.is_func:
                data_list = option.field_or_func(self.model_config, option, self, self.model_config.request)
            else:
                _field = self.model_config.model_class._meta.get_field(option.field_or_func)

                if isinstance(_field, ForeignKey):
                    data_list = FilterRow(option, self, _field.rel.model.objects.filter(option.get_condition()), self.model_config.request)
                elif isinstance(_field, ManyToManyField):
                    data_list = FilterRow(option, self, _field.rel.model.objects.filter(option.get_condition()), self.model_config.request)
                else:
                    data_list = FilterRow(option, self, _field.model.objects.filter(option.get_condition()), self.model_config.request)
            yield data_list


class AryaConfig(object):
    """
    基础配置类
    """

    """定制数据列表"""
    list_display = []

    def list_display_checkbox(self, obj=None, is_header=False):
        # obj 是表中的一条记录
        if is_header:
            tpl = "<input type='checkbox' id='headCheckBox' />"
            return mark_safe(tpl)
        else:
            tpl = "<input type='checkbox' name='pk' value='{0}' />".format(obj.pk)
            return mark_safe(tpl)

    def list_display_edit(self, obj=None, is_header=False):
        if is_header:
            return '操作'
        else:
            tpl = "<a href='{0}?{2}'>编辑</a> | <a href='{1}?{2}'>删除</a>".format(
                self.change_url(obj.pk),
                self.delete_url(obj.pk),
                self.back_url_param())
            return mark_safe(tpl)

    def get_show_list_display(self):
        list_display = []
        if self.list_display:
            list_display.extend(self.list_display)
            list_display.insert(0, AryaConfig.list_display_checkbox)
            list_display.append(AryaConfig.list_display_edit)

        return list_display

    """定制添加按钮数据列表"""
    show_add_btn = True

    def get_show_add_btn(self):
        return self.show_add_btn

    """定制Action"""
    actions = []

    def delete_action(self, request):
        """
        定制Action行为
        :param request: 
        :param queryset: 
        :return: 
        """
        pk_list = request.POST.getlist('pk')
        # self.model_class.filter(id__in=pk_list).delete()

    delete_action.short_description = "删除选择项"

    def get_actions(self):
        result = []
        result.extend(self.actions) # 添加用户自定义行为
        result.append(AryaConfig.delete_action) # 默认添加删除行为

        return result

    """ModelForm"""
    model_form = None

    def get_model_form_class(self):
        model_form_cls = self.model_form
        if not model_form_cls:
            _meta = type('Meta', (object,), {'model': self.model_class, "fields": "__all__"})
            model_form_cls = type('DynamicModelForm', (ModelForm,), {'Meta': _meta})
        return model_form_cls

    """定制查询组合条件"""
    list_filter = []

    def get_list_filter(self):
        return self.list_filter

    """定制搜索字段"""
    list_search = []

    def get_list_search(self):
        list_search = []
        list_search.extend(self.list_search)
        return list_search

    def __init__(self, model_class, site):

        self.change_filter_name = "_change_filter"
        self.popup_key = "_popup"
        self.search_key = 'q' # 搜索key
        self.search_val = None

        self.model_class = model_class
        self.app_label = model_class._meta.app_label
        self.model_name = model_class._meta.model_name

        self.site = site

        self.request = None

    def get_filter_condition(self):
        # 筛选，两种方式：基于字典，基于Q对象
        # data_list = self.model_class.objects.filter(**{}) / filter(Q())
        # 获取request.GET；剔除非数据库字段；
        params = dict(copy.deepcopy(self.request.GET))
        # {'consultant': ['6', '4'], 'gender': ['1', '2'], 'page': ['3'], 'uuu': ['999']}
        # 如果不转为字典，那么只能取到列表的最后一个值；也可以通过v = params.getlist(k)
        fields =[obj.name for obj in self.model_class._meta.get_fields()]  # 获取model中的所有字段（包含反向及关联字段）
        filter_condition = {}
        for k, v in params.items():
            if k in fields:
                key = '{k}__in'.format(k=k)  # 多选时列表中可能有多个元素，处理成双下划线
                filter_condition[key] = v

        return filter_condition

    def get_search_condition(self):
        # val = dict(copy.deepcopy(self.request.GET)).pop(self.search_key)
        params = copy.deepcopy(self.request.GET)
        search_condition = {}
        if self.search_key in params:
            val = params[self.search_key]
            self.search_val = val
            for field in self.get_list_search():
                k = '{field}__contains'.format(field=field)
                search_condition[k] = val

        return search_condition



    def changelist_view(self, request, *args, **kwargs):
        """
        列表页面
        :param request: 
        :param args: 
        :param kwargs: 
        :return: 
        """
        self.request = request
        if request.method == "POST":
            action_name = request.POST.get('action')
            action_func = getattr(self, action_name, None)
            if action_func:
                action_func(request)



        data_list = self.model_class.objects.filter(**self.get_filter_condition())\
            .filter(**self.get_search_condition()).distinct()

        # 销售显示自己的客源
        if self.model_class._meta.model_name.upper() == 'CUSTOMER':
            user_info = request.session.get('user_info')
            if user_info.get('depart_id') == 1:
                u_id = user_info.get('u_id')
                data_list = data_list.filter(consultant_id=u_id)

        cl = ChangeList(self, data_list)
        context = {
            'cl': cl,
        }
        return render(request, 'arya/change_list.html', context)

    def save(self, form, add_or_update=False):
        """
        保存
        :param form: 
        :param add_or_update: True表示添加,False表示更新 
        :return: 
        """
        return form.save()

    def add_view(self, request, *args, **kwargs):
        """
        添加页面
        :param request: 
        :param args: 
        :param kwargs: 
        :return: 
        """
        model_form_cls = self.get_model_form_class()
        popup_id = request.GET.get(self.popup_key)
        if request.method == 'GET':
            form = model_form_cls()
            return render(request, "arya/add_popup.html" if popup_id else "arya/add.html", {'form': form})
        elif request.method == "POST":
            form = model_form_cls(data=request.POST, files=request.FILES)
            if form.is_valid():
                obj = self.save(form, True)
                if obj:
                    if popup_id:
                        context = {'pk': obj.pk, 'value': str(obj), 'popup_id': popup_id}
                        return render(request, 'arya/popup_response.html', {"popup_response_data": json.dumps(context)})
                    else:
                        return redirect(self.changelist_url_params)
            return render(request, "arya/add_popup.html" if popup_id else "arya/add.html", {'form': form})

    def delete_view(self, request, pk, *args, **kwargs):
        self.model_class.objects.filter(pk=pk).delete()

        return redirect(self.changelist_url_params)

    def change_view(self, request, pk, *args, **kwargs):
        """
        修改页面
        :param request: 
        :param pk: 
        :param args: 
        :param kwargs: 
        :return: 
        """
        obj = self.model_class.objects.filter(pk=pk).first()
        if not obj:
            return redirect(self.changelist_url)
        model_form_class = self.get_model_form_class()
        if request.method == "GET":
            form = model_form_class(instance=obj)
            return render(request, 'arya/change.html', {'form': form})
        elif request.method == "POST":
            form = model_form_class(instance=obj, data=request.POST, files=request.FILES)
            if form.is_valid():
                if self.save(form, False):
                    return redirect(self.changelist_url_params)
            return render(request, 'arya/change.html', {'form': form})

    # 反向生成URL相关

    def back_url_param(self):
        query = QueryDict(mutable=True)
        if self.request.GET:
            query[self.change_filter_name] = self.request.GET.urlencode()
        return query.urlencode()

    def delete_url(self, pk):

        base_url = reverse('{0}:{1}_{2}_delete'.format(self.site.namespace, self.app_label, self.model_name),
                           args=(pk,))

        return base_url

    def change_url(self, pk):
        base_url = reverse('{0}:{1}_{2}_change'.format(self.site.namespace, self.app_label, self.model_name),
                           args=(pk,))
        return base_url

    @property
    def add_url(self):
        base_url = reverse("{0}:{1}_{2}_add".format(self.site.namespace, self.app_label, self.model_name))
        return base_url

    @property
    def add_url_params(self):
        base_url = self.add_url
        if self.request.GET:
            return base_url
        else:
            query = QueryDict(mutable=True)
            query[self.change_filter_name] = self.request.GET.urlencode()

            return "{0}?{1}".format(base_url, query.urlencode())

    @property
    def changelist_url(self):
        base_url = reverse("{0}:{1}_{2}_changelist".format(self.site.namespace, self.app_label, self.model_name))
        return base_url

    @property
    def changelist_url_params(self):
        base_url = self.changelist_url
        query = self.request.GET.get(self.change_filter_name)
        return "{0}?{1}".format(base_url, query if query else "")

    def init_request(self, func):
        import functools
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            self.request = request
            return func(request, *args, **kwargs)
        return wrapper

    def get_urls(self):
        from django.conf.urls import url

        app_model_name = self.model_class._meta.app_label, self.model_class._meta.model_name

        patterns = [
            url(r'^$', self.init_request(self.changelist_view), name="%s_%s_changelist" % app_model_name),
            url(r'^add/$', self.init_request(self.add_view), name="%s_%s_add" % app_model_name),
            url(r'^(.+)/delete/$', self.init_request(self.delete_view), name="%s_%s_delete" % app_model_name),
            url(r'^(.+)/change/$', self.init_request(self.change_view), name="%s_%s_change" % app_model_name),
        ]
        """ 装饰器初始化request:
        将装饰器写在所有视图都会交汇的位置：get_urls
        装饰器的本质就是函数，接收函数；@语法糖最终也是以上形式
        @functools.wraps(func)，显示函数的原信息（doc, __name__等）
        """
        patterns += self.extra_urls()
        return patterns

    def extra_urls(self):
        """
        扩展URL预留的钩子函数
        :return:
        """
        return []

    @property
    def urls(self):
        return self.get_urls(), None, None


class AryaSite(object):
    def __init__(self, name='arya'):
        self.name = name
        self.namespace = name
        self._registry = {}

    def register(self, model, model_config=None):
        if not model_config:
            model_config = AryaConfig
        self._registry[model] = model_config(model, self)

    def login(self, request):
        """
        登录页面逻辑
        :param request: 
        :return: 
        """
        return HttpResponse('登录页面')

    def logout(self, request):
        """
        注销页面逻辑
        :param request: 
        :return: 
        """
        return HttpResponse('注销页面')

    def get_urls(self):
        patterns = []

        from django.conf.urls import url, include
        patterns += [
            url(r'^login/', self.login),
            url(r'^logout/', self.logout),
        ]

        for model_class, model_config in self._registry.items():
            patterns += [
                url(r'^%s/%s/' % (model_class._meta.app_label, model_class._meta.model_name,), model_config.urls)
            ]

        return patterns

    @property
    def urls(self):
        return self.get_urls(), self.name, self.namespace


site = AryaSite()
