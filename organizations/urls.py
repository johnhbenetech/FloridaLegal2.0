from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^organization/(?P<organization_id>\w+)/$', views.organization, name='organization'),
    url(r'^organization/(?P<organization_id>\w+)/(?P<validation_mode>\w+)/$', views.organization, name='organization_validation'),

    url(r'^validation/(?P<organization_id>\w+)/$', views.validation, name='validation'),

    url(r'^updates/$', views.updates, name='updates'),
    url(r'^updates/(?P<is_my_update>\w+)/$', views.updates, name='my_updates'),
]