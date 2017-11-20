from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^accounts/login/$', views.login_view, name='login'),
    url(r'^accounts/logout/$', views.logout_view, name='logout'),
]