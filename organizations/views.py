from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, HttpResponseRedirect, HttpResponse, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib import messages
from .models import *
from services.models import Service, ServiceUpdate
from .forms import OrganizationForm, OrganizationUpdateForm, UpdateForm
from services.forms import ServiceForm, ServiceUpdateForm
from django.forms.models import modelformset_factory
from django.forms import model_to_dict
from django.contrib.contenttypes.models import ContentType
from services.models import *


@login_required()
def home(request, organization_id=None):
    user = request.user
    data = request.GET
    if not organization_id:
        organization_id = data.get("organization") if data.get("organization") != "" else None

    if organization_id:
        organization_id = data.get("organization")
        return HttpResponseRedirect(reverse("organization", kwargs={"organization_id": organization_id}))

    return render(request, 'organizations/home.html', locals())


@login_required()
def organization(request, organization_id=None, validation_mode=None):
    statuses = STATUS_CHOICES

    page = "organization"

    print(request.session.get("pages", "no"))
    if not "pages" in request.session:
        request.session["pages"] = [request.META.get('HTTP_REFERER')]
    else:
        request.session["pages"].append(request.session["pages"])

    user = request.user
    if validation_mode=="validation_mode":
        validation_mode = True
        if not user.is_superuser:
            return HttpResponseRedirect(reverse("home"))
    else:
        validation_mode = False

    is_organization_update_exists = False
    if organization_id:
        if user.is_superuser:
            organization = get_object_or_404(Organization, id=organization_id)
        else:
            organization = get_object_or_404(Organization, id=organization_id, owner=user)
        organization_update = OrganizationUpdate.objects.filter(organization_id=organization_id, is_processed=False)
        if organization_update:
            organization_update = organization_update.last()
            form = OrganizationUpdateForm(request.POST or None, instance=organization_update)
            is_organization_update_exists = True
        else:
            form = OrganizationForm(request.POST or None, instance=organization)

        initial_data = model_to_dict(organization)
    else:
        return HttpResponseRedirect(reverse("home"))

    if request.POST:
        data = request.POST
        if form.is_valid():
            if is_organization_update_exists:
                new_form = form.save(commit=False)
                new_form = form.save()
            else:
                organization_update_data = form.cleaned_data
                organization_update_data["organization"] = organization
                organization_update_data["owner"] = organization.owner
                organization_update = OrganizationUpdate.objects.create(**organization_update_data)
                form = OrganizationUpdateForm(request.POST or None, instance=organization_update)

            Update.objects.get_or_create(organization=organization, update_status="Unprocessed")

    if validation_mode:
        pending_updates = Update.objects.filter(organization=organization, update_status="Unprocessed").exists()

    return render(request, 'organizations/organization.html', locals())


@login_required()
def validation(request, organization_id):
    validation_mode = True
    page = "validation"
    user = request.user
    if not user.is_superuser:
            return HttpResponseRedirect(reverse("home"))

    try:
        update = Update.objects.get(organization_id=organization_id, update_status="Unprocessed")
    except:
        return HttpResponseRedirect(reverse("updates"))

    form = UpdateForm(request.POST or None, instance=update)
    if request.POST:
        if form.is_valid():
            new_form = form.save(commit=False)
            new_form.save()

            if user.is_superuser:
                #put here model names, which will be iterated for finding updates
                models = ["OrganizationUpdate", "LocationUpdate", "ProgramUpdate", "ServiceUpdate", "EligibilityUpdate"]
                connection_fields_mapping = {"OrganizationUpdate": "organization_id", "LocationUpdate": "organization_id",
                                             "ProgramUpdate": "organization_id",
                                             "ServiceUpdate": "program__organization_id",
                                             "EligibilityUpdate": "service__program__organization_id"
                                             }
                for model_name in models:
                    model_update_class = globals()[model_name]

                    model_initial_name = model_name.split("Update")[0]
                    model_initial_class = globals()[model_initial_name]
                    content_type = ContentType.objects.get_for_model(model_initial_class)
                    connection_field_name = content_type.model#the same as connection field name (service, program)

                    kwargs = dict()
                    kwargs["is_processed"] = False
                    kwargs[connection_fields_mapping[model_name]] = organization_id
                    objects_update = model_update_class.objects.filter(**kwargs)

                    fields_to_exclude = ["created_by", "created", "modified", "update_status", "is_processed",
                                         "is_marked_deleted", "id", "owner"]

                    if user.is_superuser and new_form.update_status == "Accepted":
                        for item_update in objects_update:
                            object_update_dictionary = model_to_dict(item_update, exclude=fields_to_exclude)

                            #excluding many to many relation fields from the dictionary and applying them after object is created
                            object_update_dictionary_for_creation = dict()
                            values_m2m = dict()
                            for field_name, val in object_update_dictionary.items():
                                if val:
                                    if model_update_class._meta.get_field(field_name).get_internal_type() == "ForeignKey":
                                        field_name = "%s_id" % field_name

                                    if type(val).__name__ == "QuerySet":
                                        values_m2m[field_name] = val
                                    else:
                                        object_update_dictionary_for_creation[field_name] = val

                            if getattr(item_update, connection_field_name):
                                if item_update.is_marked_deleted:
                                    linking_field_id = getattr(item_update, connection_field_name).id
                                    model_initial_class.objects.filter(id=linking_field_id).delete()
                                else:
                                    object_initial = getattr(item_update, connection_field_name)
                                    for field_name, value in object_update_dictionary.items():
                                        if model_update_class._meta.get_field(field_name).get_internal_type() == "ForeignKey":
                                            field_name = "%s_id" % field_name
                                        setattr(object_initial, field_name, value)
                                    object_initial.save()
                            else:
                                new_object = model_initial_class.objects.create(**object_update_dictionary_for_creation)
                                for field, val in values_m2m.items():
                                    getattr(new_object, field).set(val)

                                #linking created item to the update instance
                                setattr(item_update, connection_field_name, new_object)
                                item_update.save(force_update=True)

                    if user.is_superuser and new_form.update_status in ("Accepted", "Rejected"):
                        #mark updated objects as processed
                        objects_update.update(is_processed=True)

    return render(request, 'organizations/validation.html', locals())


@login_required()
def updates(request, is_my_update=None):
    user = request.user
    if user.is_superuser:
        if is_my_update == "my":
            updates = Update.objects.filter(organization__owner=user).order_by("-id")
        else:
            updates = Update.objects.all().order_by("-id")
    else:
        updates = Update.objects.filter(organization__owner=user).order_by("-id")
    return render(request, 'organizations/updates.html', locals())
