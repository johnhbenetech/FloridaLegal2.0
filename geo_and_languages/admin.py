from django.contrib import admin
from .models import *


class LanguageAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Language._meta.fields]

    class Meta:
        model = Language

admin.site.register(Language, LanguageAdmin)


class CountyAdmin(admin.ModelAdmin):
    list_display = [field.name for field in County._meta.fields]

    class Meta:
        model = County

admin.site.register(County, CountyAdmin)
