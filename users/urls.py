from django.conf.urls import url, include
from rest_framework.authtoken.views import obtain_auth_token
from . import views
from .views import TokenGetView

urlpatterns = [
    url(r'^accounts/login/$', views.login_view, name='login'),
    url(r'^accounts/logout/$', views.logout_view, name='logout'),
    url(r'^get/$', TokenGetView.as_view(), name='get'),
    url(r'^accounts/auth/$', obtain_auth_token),
]