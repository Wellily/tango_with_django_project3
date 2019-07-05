from django.shortcuts import render, reverse, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from rango2.models import Category, Page, UserProfile
from rango2.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from datetime import datetime


# 主页视图
def index(request):
    request.session.set_test_cookie()
    context_dict = {}
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context_dict['categories'] = category_list
    context_dict['pages'] = page_list

    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']
    response = render(request, 'rango2/index.html', context_dict)
    return response

    # return render(request, 'rango2/index.html', context_dict)


def show_category(request, category_name_slug):
    context_dict = {}
    try:
        category = Category.objects.get(slug=category_name_slug)
        pages = Page.objects.filter(category=category).order_by('-views')
        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        context_dict['category'] = None
        context_dict['pages'] = None
    return render(request, 'rango2/category.html', context_dict)


def add_category(request):
    form = CategoryForm()  # 创建一个类别表单对象

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            c = form.save(commit=True)
            print(c, c.slug)
            return index(request)
        else:
            print(form.errors)

    return render(request, 'rango2/add_category.html', {'form': form})


@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    form = PageForm()
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.save()
                return show_category(request, category_name_slug)
        else:
            print(form.errors)

    return render(request, 'rango2/add_page.html', {'form': form, 'category': category})


@login_required
def register_profile(request):
    form = UserProfileForm()
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            user_profile = form.save(commit=False)
            user_profile.user = request.user
            user_profile.save()
            return redirect('rango2:index')
        else:
            print(form.errors)
    contex_dict = {'form': form}
    return render(request, 'rango2/profile_registration.html', contex_dict)


@login_required
def profile(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return redirect('rango2:index')

    userprofile = UserProfile.objects.get_or_create(user=user)[0]
    form = UserProfileForm(
        {'website': userprofile.website, 'picture': userprofile.picture}
    )

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if form.is_valid():
            form.save(commit=True)
            return redirect('rango2:profile', user.username)
        else:
            print(form.errors)
    return render(request, 'rango2/profile.html', {'userprofile':userprofile, 'selecteduser': user, 'form':form})


def register(request):
    registered = False  # 模板是否注册成功
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)  # 和之前的form = CategoryForm(request.POST)有何区别？
        profile_form = UserProfileForm(data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()  # 为什么之前的要page = form.save(commit=False)
            user.set_password(user.password)  # 计算密码哈希值，更新User对象
            user.save()

            profile = profile_form.save(commit=False)  # 因为要处理一对一的外键，所以False
            profile.user = user
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            profile.save()
            registered = True
        else:
            print(user_form.errors, profile_form.errors)  # 数据无效，在终端打印问题
    else:  # 如果不是POST请求，生成空表单，进行渲染
        user_form = UserForm()
        profile_form = UserProfileForm()

    context_dict = {}
    context_dict['user_form'] = user_form
    context_dict['profile_form'] = profile_form
    context_dict['registered'] = registered
    return render(request, 'rango2/register.html', context_dict)


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('rango2:index'))
            else:
                return HttpResponse("Your Rango2 account is disabled.")
        else:
            # 提供的凭据有问题，用户名或者密码不正确
            print("Invalid login details:{0}, {1}".format(username, password))
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, 'rango2/login.html', {})


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('rango2:index'))


def about(request):
    return render(request, 'rango2/about.html', {})


def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val


def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits', '1'))
    last_visit_cookie = get_server_side_cookie(request, 'last_visits', str(datetime.now()))  # cookie是字符串
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')  # 所以自行转换为时间
    if (datetime.now() - last_visit_time).seconds > 0:
        visits = visits+1
        request.session['last_visits'] = str(datetime.now())
    else:
        request.session['last_visits'] = last_visit_cookie
    request.session['visits'] = visits


def track_url(request):
    page_id = None
    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']
            page = Page.objects.get(id=page_id)
            if page:
                page.views = page.views + 1
                page.save()
                return HttpResponseRedirect(page.url)
    return HttpResponseRedirect(reverse('rango2:index'))


# 这是没有使用到ajax的局部刷新的方法，是刷新了整个页面的方法，不太友好
@login_required
def like_category(request):
    cat_id = None
    if request.method == 'GET':
        cat_id = request.GET['category_id']
        likes = 0
        if cat_id:
            cat = Category.objects.get(id=int(cat_id))
            if cat:
                likes = cat.likes + 1
                cat.likes = likes
                cat.save()
    # return HttpResponseRedirect(reverse("rango2:show_category", kwargs={'category_name_slug': cat.slug}))
    return HttpResponse(likes)


@login_required
def like_category1(request):
    cat_id = None
    if request.method == 'GET':
        cat_id = request.GET['category_id']
        likes = 0
        if cat_id:
            cat = Category.objects.get(id=int(cat_id))
            if cat:
                likes = cat.likes + 1
                cat.likes = likes
                cat.save()
            data = {'code': 200, 'hint': '操作成功'}
    return JsonResponse(data)


"""
# 客户端存储网站主页访问次数
def visitor_cookie_handler(request, response):
    visits = int(request.COOKIES.get('visits', '1'))
    last_visit_cookie = request.COOKIES.get('last_visit', str(datetime.now()))  # cookie是字符串
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')  # 所以自行转换为时间
    if (datetime.now() - last_visit_time).seconds > 0:
        visits = visits+1
        response.set_cookie('last_visit', str(datetime.now()))  # 如果该cookie不存在，会自动创建
    else:
        response.set_cookie('last_visit', str(datetime.now()))
    response.set_cookie('visits', visits)
"""

