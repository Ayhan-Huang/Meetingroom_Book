from django.shortcuts import render, redirect
from rbac.service.init_permission import init_permission
from rbac import models


def login(request):
    if request.method == "GET":
        return render(request, "login.html")
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_obj = models.User.objects.filter(username=username, password=password).first()
        if not user_obj:
            return render(request, "login.html", {'error': '用户名或密码错误！'})
        else:
            init_permission(request, user_obj)
            # # 写入用户信息到session中，用于展示销售客源；从app01 的 userinfo表反查
            # request.session['user_info'] = {'u_id': user_obj.userinfo.pk, 'depart_id': user_obj.userinfo.depart_id}
            return redirect('/arya/rbac/permission/')

