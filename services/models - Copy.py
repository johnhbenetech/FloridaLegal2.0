from django.db import models
from organizations.models import Organization
from django.contrib.auth.models import User
from geo_and_languages.models import Language, County
from django.core.validators import RegexValidator
from django.db.models import Q
from crequest.middleware import CrequestMiddleware
from django.db.models.signals import post_save
from utils.helpers import CreationUpdatedInstances


class Program(models.Model, CreationUpdatedInstances):
    name = models.CharField(max_length=255,blank=False)
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL,blank=False,null=True)
    taxonomy_ids = models.ManyToManyField("Taxonomy", blank=True)
    created_by = models.ForeignKey(User, blank=True, null=True, default=None)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    exclude_fields_for_update = ["created_by", "created", "modified"]

    def __str__(self):
        return "%s" % self.id

    def save(self, *args, **kwargs):
        current_request = CrequestMiddleware.get_request()
        if current_request and (not self.created_by or not self.pk):
            user = current_request.user
            self.created_by = user
        super(Program, self).save(*args, **kwargs)


class ProgramUpdate(models.Model):
    program = models.ForeignKey(Program, blank=True, null=True, default=None)
    name = models.CharField(max_length=255,blank=False)
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL,blank=False,null=True)
    taxonomy_ids = models.ManyToManyField("Taxonomy", blank=True)
    created_by = models.ForeignKey(User, blank=True, null=True, default=None)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    is_processed = models.BooleanField(default=False)
    is_marked_deleted = models.BooleanField(default=False)

    def __str__(self):
        return "%s" % self.id

    def save(self, *args, **kwargs):
        current_request = CrequestMiddleware.get_request()
        if current_request and (not self.created_by or not self.pk):
            user = current_request.user
            self.created_by = user
        
        super(ProgramUpdate, self).save(*args, **kwargs)
        
        
def programupdate_post_save(sender, instance, created, **kwargs):
    #assigning related services for newly created ProgramUpdate instance
    #It is needed for 2nd and 3rd level children
    if instance.program:

        if instance.program.service_set.all().exists():
            services = instance.program.service_set.all()
            for service in services:
                service.program = instance.program
                service.program_update = instance
                service.save(force_update=True)

        if instance.program.serviceupdate_set.filter(is_marked_deleted=False, is_processed=False, program_update__isnull=True).exists():
            services = instance.program.serviceupdate_set.filter(is_marked_deleted=False, is_processed=False, program_update__isnull=True)
            for service in services:
                service.program_update = instance
                service.save(force_update=True)

        if instance.serviceupdate_set.filter(is_marked_deleted=False, is_processed=False, program__isnull=True).exists():
            services = instance.serviceupdate_set.filter(is_marked_deleted=False, is_processed=False, program__isnull=True)
            for service in services:
                service.program = instance.program
                service.save(force_update=True)

post_save.connect(programupdate_post_save, sender=ProgramUpdate)


class Service(models.Model, CreationUpdatedInstances):
    program = models.ForeignKey(Program, blank=True, null=True, default=None)
    program_update = models.ForeignKey(ProgramUpdate, blank=True, null=True, default=None)
    name = models.CharField(max_length=255,blank=False)
    description = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    status = models.CharField(max_length=255,blank=True)
    interpretation_services = models.ManyToManyField(Language, blank=True)
    application_process = models.CharField(max_length=255,blank=True)
    taxonomy_ids = models.ManyToManyField("Taxonomy",blank=True)
    created_by = models.ForeignKey(User,blank=True, null=True, default=None)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    exclude_fields_for_update = ["created_by", "created", "modified"]

    def __str__(self):
        return "%s" % self.id

    def save(self, *args, **kwargs):
        current_request = CrequestMiddleware.get_request()
        if current_request and (not self.created_by or not self.pk):
            user = current_request.user
            self.created_by = user
        super(Service, self).save(*args, **kwargs)


class ServiceUpdate(models.Model):
    service = models.ForeignKey(Service, blank=True, null=True, default=None)
    program = models.ForeignKey(Program, blank=True, null=True, default=None)
    program_update = models.ForeignKey(ProgramUpdate, blank=True, null=True, default=None)
    name = models.CharField(max_length=255,blank=False)
    description = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    status = models.CharField(max_length=255,blank=True)
    interpretation_services = models.ManyToManyField(Language, blank=True)
    application_process = models.CharField(max_length=255,blank=True)
    taxonomy_ids = models.ManyToManyField("Taxonomy",blank=True)
    created_by = models.ForeignKey(User,blank=True, null=True, default=None)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    is_processed = models.BooleanField(default=False)
    is_marked_deleted = models.BooleanField(default=False)

    def __str__(self):
        return "%s" % self.id

    def save(self, *args, **kwargs):
        current_request = CrequestMiddleware.get_request()
        if current_request and (not self.created_by or not self.pk):
            user = current_request.user
            self.created_by = user

        super(ServiceUpdate, self).save(*args, **kwargs)


def serviceupdate_post_save(sender, instance, created, **kwargs):
    #assigning related services for newly created ProgramUpdate instance
    #It is needed for 2nd and 3rd level children
    if instance.service:

        if instance.service.eligibility_set.all().exists():
            eligibilities = instance.service.eligibility_set.all()
            for eligibility in eligibilities:
                eligibility.service = instance.service
                eligibility.service_update = instance
                eligibility.save(force_update=True)

        if instance.service.eligibilityupdate_set.filter(is_marked_deleted=False, is_processed=False, service_update__isnull=True).exists():
            eligibilities = instance.service.eligibilityupdate_set.filter(is_marked_deleted=False, is_processed=False, service_update__isnull=True)
            for eligibility in eligibilities:
                eligibility.service_update = instance
                eligibility.save(force_update=True)

        if instance.eligibilityupdate_set.filter(is_marked_deleted=False, is_processed=False, service__isnull=True).exists():
            eligibilities = instance.eligibilityupdate_set.filter(is_marked_deleted=False, is_processed=False, service__isnull=True)
            for eligibility in eligibilities:
                eligibility.service = instance.service
                eligibility.save(force_update=True)

post_save.connect(serviceupdate_post_save, sender=ServiceUpdate)


class Eligibility(models.Model, CreationUpdatedInstances):
    service = models.ForeignKey(Service, blank=True, null=True, default=None)
    service_update = models.ForeignKey(ServiceUpdate, blank=True, null=True, default=None)

    eligibility_details = models.TextField(blank=True)
    minimum_age = models.TextField(blank=True)
    maximum_age = models.TextField(blank=True)
    veteran_status = models.TextField(blank=True)
    maximum_income= models.TextField(blank=True)
    taxonomy = models.ManyToManyField("Taxonomy",blank=True)
    taxonomy_detail = models.TextField(blank=True)
    area = models.ManyToManyField(County, blank=True)
    area_description = models.TextField(blank=True)
    required_document = models.TextField(blank=True)

    exclude_fields_for_update = []


class EligibilityUpdate(models.Model):
    eligibility = models.ForeignKey(Eligibility, blank=True, null=True, default=None)
    service = models.ForeignKey(Service, blank=True, null=True, default=None)
    service_update = models.ForeignKey(ServiceUpdate, blank=True, null=True, default=None)

    eligibility_details = models.TextField(blank=True)
    minimum_age = models.TextField(blank=True)
    maximum_age = models.TextField(blank=True)
    veteran_status = models.TextField(blank=True)
    maximum_income= models.TextField(blank=True)
    taxonomy = models.ManyToManyField("Taxonomy",blank=True)
    taxonomy_detail = models.TextField(blank=True)
    area = models.ManyToManyField(County, blank=True)
    area_description = models.TextField(blank=True)
    required_document = models.TextField(blank=True)
    is_processed = models.BooleanField(default=False)
    is_marked_deleted = models.BooleanField(default=False)


class Taxonomy(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ('name', )

    def __str__(self):
        return self.name





