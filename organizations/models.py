from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
import select2.fields
from django.db.models import Q
from geo_and_languages.models import Language
from crequest.middleware import CrequestMiddleware
from utils.helpers import CreationUpdatedInstances


class Organization(models.Model, CreationUpdatedInstances):
    name = models.CharField(max_length=255,blank=False)
    description = models.TextField(blank=True)
    url = models.CharField(max_length=255,verbose_name="Website URL",blank=True)
    email = models.EmailField(blank=True)
    owner = models.ForeignKey(User, related_name='service_owner', blank=False)
    created_by = models.ForeignKey(User,blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    exclude_fields_for_update = ["created_by", "created", "modified", "owner"]

    def __str__(self):
        return "%s" % self.id

    def save(self, *args, **kwargs):
        current_request = CrequestMiddleware.get_request()
        if current_request and (not self.created_by or not self.pk):
            user = current_request.user
            self.created_by = user
        super(Organization, self).save(*args, **kwargs)


class OrganizationUpdate(models.Model):
    organization = models.ForeignKey(Organization)
    name = models.CharField(max_length=255,blank=False)
    description = models.TextField(blank=True)
    url = models.CharField(max_length=255,verbose_name="Website URL",blank=True)
    email = models.EmailField(blank=True)
    owner = models.ForeignKey(User, related_name='service_owner_upd', blank=True, null=True, default=None)
    created_by = models.ForeignKey(User, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    is_processed = models.BooleanField(default=False)
    is_marked_deleted = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        current_request = CrequestMiddleware.get_request()
        if current_request and (not self.created_by or not self.pk):
            user = current_request.user
            self.created_by = user
        super(OrganizationUpdate, self).save(*args, **kwargs)


STATUS_CHOICES = (
    ("Accepted", 'Accepted'),
    ("Rejected", 'Rejected'),
    ("Unprocessed", 'Unprocessed'),
)


class Update(models.Model):
    organization = models.ForeignKey(Organization)
    validation_note = models.TextField(null=True)
    update_status = models.CharField(max_length=30,choices=STATUS_CHOICES, default="Unprocessed")
    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now=True, null=True)


STATE_PROVINCE_CHOICES = (('AL', 'Alabama'), ('AZ', 'Arizona'), ('AR', 'Arkansas'), ('CA', 'California'), ('CO', 'Colorado'), ('CT', 'Connecticut'), ('DE', 'Delaware'), ('DC', 'District of Columbia'), ('FL', 'Florida'), ('GA', 'Georgia'), ('ID', 'Idaho'), ('IL', 'Illinois'), ('IN', 'Indiana'), ('IA', 'Iowa'), ('KS', 'Kansas'), ('KY', 'Kentucky'), ('LA', 'Louisiana'), ('ME', 'Maine'), ('MD', 'Maryland'), ('MA', 'Massachusetts'), ('MI', 'Michigan'), ('MN', 'Minnesota'), ('MS', 'Mississippi'), ('MO', 'Missouri'), ('MT', 'Montana'), ('NE', 'Nebraska'), ('NV', 'Nevada'), ('NH', 'New Hampshire'), ('NJ', 'New Jersey'), ('NM', 'New Mexico'), ('NY', 'New York'), ('NC', 'North Carolina'), ('ND', 'North Dakota'), ('OH', 'Ohio'), ('OK', 'Oklahoma'), ('OR', 'Oregon'), ('PA', 'Pennsylvania'), ('RI', 'Rhode Island'), ('SC', 'South Carolina'), ('SD', 'South Dakota'), ('TN', 'Tennessee'), ('TX', 'Texas'), ('UT', 'Utah'), ('VT', 'Vermont'), ('VA', 'Virginia'), ('WA', 'Washington'), ('WV', 'West Virginia'), ('WI', 'Wisconsin'), ('WY', 'Wyoming'),('AK', 'Alaska'), ('HI', 'Hawaii'))

class Location(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, blank=False,null=True)
    name = models.CharField(max_length=255,blank=True)
    description = models.TextField(blank=True)
    transportation = models.TextField(blank=True)
    latitude = models.CharField(max_length=15,blank=True)
    longitude = models.CharField(max_length=15,blank=True)
    address_1 = models.CharField(max_length=255, blank=True)
    address_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    state_province = models.CharField(max_length=2,choices=STATE_PROVINCE_CHOICES,null=True, blank=True)
    postal_code = models.CharField(max_length=255, blank=True)


class LocationUpdate(models.Model):
    location = models.ForeignKey(Location, blank=True, null=True, default=None)
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, blank=False,null=True)
    name = models.CharField(max_length=255,blank=True)
    description = models.TextField(blank=True)
    transportation = models.TextField(blank=True)
    latitude = models.CharField(max_length=15,blank=True)
    longitude = models.CharField(max_length=15,blank=True)
    address_1 = models.CharField(max_length=255, blank=True)
    address_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    state_province = models.CharField(max_length=2,choices=STATE_PROVINCE_CHOICES,null=True, blank=True)
    postal_code = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(User, blank=True, null=True, default=None)
    is_processed = models.BooleanField(default=False)
    is_marked_deleted = models.BooleanField(default=False)


PHONE_TYPE_CHOICES = (('fixed', 'Fixed'), ('cell', 'Cellular'),('fax','Fax'), ('hotline','Hotline'))
# Parent: Location
class Contact(models.Model):
    location = models.ForeignKey(Location, blank=True, null=True, default=None)
    contact_name = models.CharField(max_length=255, blank=True)
    contact_title = models.CharField(max_length=255, blank=True)
    contact_department = models.CharField(max_length=255, blank=True)
    contact_email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=255, blank=True, validators=[
        RegexValidator(
            regex='^\([0-9][0-9][0-9]\)[0-9][0-9][0-9]\-[0-9][0-9][0-9][0-9]$',
            message='Phone format must be (555)555-5555',
        ),
    ])
    phone_extension = models.CharField(max_length=255, blank=True)
    phone_type = models.CharField(max_length=10, choices=PHONE_TYPE_CHOICES, blank=True)
    phone_department = models.CharField(max_length=255, blank=True)
    phone_languages = select2.fields.ManyToManyField(Language, blank=True, ajax=True,
                                               search_field=lambda q: Q(code__icontains=q) | Q(name__icontains=q))


class ContactUpdate(models.Model):
    contact = models.ForeignKey(Contact)
    contact_name = models.CharField(max_length=255, blank=True)
    contact_title = models.CharField(max_length=255, blank=True)
    contact_department = models.CharField(max_length=255, blank=True)
    contact_email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=255, blank=True, validators=[
        RegexValidator(
            regex='^\([0-9][0-9][0-9]\)[0-9][0-9][0-9]\-[0-9][0-9][0-9][0-9]$',
            message='Phone format must be (555)555-5555',
        ),
    ])
    phone_extension = models.CharField(max_length=255, blank=True)
    phone_type = models.CharField(max_length=10, choices=PHONE_TYPE_CHOICES, blank=True)
    phone_department = models.CharField(max_length=255, blank=True)
    phone_languages = select2.fields.ManyToManyField(Language, blank=True, ajax=True,
                                               search_field=lambda q: Q(code__icontains=q) | Q(name__icontains=q))

    is_processed = models.BooleanField(default=False)
    is_marked_deleted = models.BooleanField(default=False)
