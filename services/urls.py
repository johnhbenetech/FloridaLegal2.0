from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^editing/(?P<organization_id>\w+)/(?P<page_name>\w+)/$', views.EditingView.as_view(), name='editing'),
    url(r'^editing/(?P<organization_id>\w+)/(?P<page_name>\w+)/(?P<validation_mode>\w+)/$', views.EditingView.as_view(),
        name='editing_validation'),

    url(r'^editing_related_objects/(?P<organization_id>\w+)/(?P<page_name>\w+)/(?P<parent_model>\w+)/(?P<parent_obj_id>\w+)/$',
        views.EditingView.as_view(), name='editing_related_objects'),
    url(r'^editing_related_objects/(?P<organization_id>\w+)/(?P<page_name>\w+)/(?P<parent_model>\w+)/(?P<parent_obj_id>\w+)/(?P<validation_mode>\w+)/$',
        views.EditingView.as_view(), name='editing_related_objects_validation'),
]