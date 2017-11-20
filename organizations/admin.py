from django.contrib import admin
from .models import *


class OrganizationAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Organization._meta.fields]
    readonly_fields = ["created_by"]

    class Meta:
        model = Organization

admin.site.register(Organization, OrganizationAdmin)


class OrganizationUpdateAdmin(admin.ModelAdmin):
    list_display = [field.name for field in OrganizationUpdate._meta.fields]
    readonly_fields = ["created_by"]

    class Meta:
        model = OrganizationUpdate

admin.site.register(OrganizationUpdate, OrganizationUpdateAdmin)


class LocationAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Location._meta.fields]

    class Meta:
        model = Location

admin.site.register(Location, LocationAdmin)


class LocationUpdateAdmin(admin.ModelAdmin):
    list_display = [field.name for field in LocationUpdate._meta.fields]
    readonly_fields = ["created_by"]

    class Meta:
        model = LocationUpdate

admin.site.register(LocationUpdate, LocationUpdateAdmin)


class ContactAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Contact._meta.fields]

    class Meta:
        model = Contact

admin.site.register(Contact, ContactAdmin)


class ContactUpdateAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ContactUpdate._meta.fields]

    class Meta:
        model = ContactUpdate

admin.site.register(ContactUpdate, ContactUpdateAdmin)


class UpdateAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Update._meta.fields]

    class Meta:
        model = Update

admin.site.register(Update, UpdateAdmin)