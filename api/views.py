from rest_framework.permissions import (
    IsAuthenticated,
    )

from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from organizations.models import *
from .serializers import *


class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ('get', "put", "post", "patch")
    is_update_model = False

    
    
    def get_queryset(self):
        user = self.request.user
        instance_id = self.kwargs.get("pk")
        queryset = Organization.objects.all()
#        queryset = Organization.objects.filter(owner=user, id=instance_id)
        if instance_id is not None:
            if user.is_superuser:
                queryset = queryset.filter(id=instance_id)
            else:
                queryset = queryset.filter(owner=user, id=instance_id)
        return queryset    
    
    
    
    
#    def get_queryset(self):
#        user = self.request.user
#        instance_id = self.kwargs.get("pk")
#
#        if instance_id:
#            obj = Organization.objects.filter(owner=user, pk=instance_id)
#            print(obj)
#            if obj:
#                qs = OrganizationUpdate.objects.filter(organization__owner=user)
#                self.is_update_model = True
#                self.kwargs["pk"] = obj.id
#            else:
#                qs = Organization.objects.filter(owner=user)
#        else:
#            qs = Organization.objects.filter(owner=user)
#        qs = Organization.objects.filter(owner=user)
#        return qs

    def get_serializer(self, args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        if self.is_update_model:
            serializer_class = OrganizationUpdateSerializer
        else:
            serializer_class = OrganizationSerializer
        return serializer_class(args, **kwargs)
