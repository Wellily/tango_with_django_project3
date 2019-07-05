from django.urls import path, re_path
from rango2 import views

app_name='rango2'
urlpatterns = [
    re_path('^$', views.index, name='index'),
    re_path('^about/', views.about, name='about'),
    re_path("^category/(?P<category_name_slug>[\w\-]+)/$", views.show_category, name='show_category'),
    re_path('^add_category/', views.add_category, name='add_category'),
    re_path('^category/(?P<category_name_slug>[\w\-]+)/add_page/$', views.add_page, name='add_page'),
    re_path('^goto/', views.track_url, name='goto'),
    re_path('^register_profile/$', views.register_profile, name='register_profile'),
    re_path('^profile/(?P<username>[\w\-]+)/$', views.profile, name='profile'),
    re_path('^like/$', views.like_category, name='like_category')
    # re_path('^register/', views.register, name='register'),
    # re_path('^login/', views.user_login, name='login'),
    # re_path('^logout/', views.user_logout, name='logout'),
]