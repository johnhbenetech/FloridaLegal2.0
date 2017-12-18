from django.contrib import admin
from .models import *
from easy_select2 import select2_modelform



class ProgramAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Program._meta.fields]
    readonly_fields = ["created_by"]

    class Meta:
        model = Program

admin.site.register(Program, ProgramAdmin)


class ProgramUpdateAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ProgramUpdate._meta.fields]
    readonly_fields = ["created_by"]

    class Meta:
        model = ProgramUpdate

admin.site.register(ProgramUpdate, ProgramUpdateAdmin)



ServiceForm = select2_modelform(Service, attrs={'width': '275px'})

class ServiceAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Service._meta.fields]
    readonly_fields = ["created_by"]
    form = ServiceForm
    class Meta:
        model = Service

admin.site.register(Service, ServiceAdmin)


class ServiceUpdateAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ServiceUpdate._meta.fields]
    readonly_fields = ["created_by"]

    class Meta:
        model = ServiceUpdate

admin.site.register(ServiceUpdate, ServiceUpdateAdmin)


class EligibilityAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Eligibility._meta.fields]

    class Meta:
        model = Eligibility

admin.site.register(Eligibility, EligibilityAdmin)


class EligibilityUpdateAdmin(admin.ModelAdmin):
    list_display = [field.name for field in EligibilityUpdate._meta.fields]

    class Meta:
        model = EligibilityUpdate

admin.site.register(EligibilityUpdate, EligibilityUpdateAdmin)




class ApplicationProcessAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ApplicationProcess._meta.fields]

    class Meta:
        model = ApplicationProcess

admin.site.register(ApplicationProcess, ApplicationProcessAdmin)


class ApplicationProcessUpdateAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ApplicationProcessUpdate._meta.fields]

    class Meta:
        model = ApplicationProcessUpdate

admin.site.register(ApplicationProcessUpdate, ApplicationProcessUpdateAdmin)




class TaxonomyAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Taxonomy._meta.fields]

    class Meta:
        model = Taxonomy

admin.site.register(Taxonomy, TaxonomyAdmin)