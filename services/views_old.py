from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, HttpResponseRedirect, HttpResponse, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib import messages
from services.models import Service, ServiceUpdate, Program, ProgramUpdate
from .forms import ServiceForm, ServiceUpdateForm, ProgramForm, ProgramUpdateForm
from organizations.forms import *
from django.forms.models import modelformset_factory
from organizations.models import Organization
from django.forms import model_to_dict
from organizations.models import Update
from django.contrib.contenttypes.models import ContentType


login_required()
def editing(request, organization_id, page_name, validation_mode=None):
    """
    It is assumed that page_name has a name of model with "update" word at the end in plural form ("services") starting with a lowcase symbol
    """
    user = request.user
    page = page_name

    #for back button
    previous_url = request.META.get('HTTP_REFERER')

    if validation_mode=="validation_mode":
        validation_mode = True
        if not user.is_superuser:
            return HttpResponseRedirect(reverse("home"))
    else:
        validation_mode = False


    if user.is_superuser:
        organization = get_object_or_404(Organization, id=organization_id)
    else:
        organization = get_object_or_404(Organization, id=organization_id, owner=user)
    model_name_initial = page_name[:-1].lower()
    content_type = ContentType.objects.get(model=model_name_initial.lower())
    model_initial_class = content_type.model_class()
    model_initial_class_name = model_initial_class.__name__
    form_initial_name = "%sForm" % model_initial_class_name
    form_initial_class = globals()[form_initial_name]
    model_update_class_name = "%sUpdate" % model_initial_class_name
    model_update_class = globals()[model_update_class_name]

    form_update_class_name = "%sForm" % model_update_class_name
    form_update_class = globals()[form_update_class_name]

    #Programs formset creation based on Program or ProgramUpdate models
    is_update_objects = False
    objects_initial = model_initial_class.objects.filter(organization=organization).order_by("-id")

    #all the programs_update including those one which have pending is_marked_deleted=True
    objects_update = model_update_class.objects.filter(organization=organization, is_processed=False).order_by("id")
    if objects_update:
        is_update_objects = True

        #So there are existing programs to update
        # here it is a check if there are any not edited instances of programs
        # and creating ProgramUpdate instances for them
        if objects_initial:
            objects_in_update_ids = [getattr(item, model_name_initial).id if getattr(item, model_name_initial) else None for item in objects_update]
            objects_to_add = objects_initial.exclude(id__in=objects_in_update_ids).values()
            if objects_to_add:
                for object_to_add in objects_to_add:
                    fields_to_exclude = ["id", "created", "modified"]
                    fields_to_exclude.append(model_name_initial)

                    #maybe to remake this later as a model method
                    update_kwargs = dict()
                    for field_name, val in object_to_add.items():
                        if not field_name in fields_to_exclude:
                            update_kwargs[field_name] = val
                        update_kwargs[model_name_initial] = object

                    related_obj = model_initial_class.objects.get(id=object_to_add["id"])
                    update_kwargs[ model_name_initial] = related_obj
                    model_update_class.objects.create(**update_kwargs)

        #getting programs_update with the recently added instances + filtering all instances with is_marked_deleted = False
        objects_update = model_update_class.objects.filter(organization=organization, is_marked_deleted=False, is_processed=False)\
            .order_by("-id")
        main_formset = modelformset_factory(model_update_class, form=form_update_class, extra=0, can_delete=True)
        formset = main_formset(queryset=objects_update, prefix='object_prefix')
    else:
        main_formset = modelformset_factory(model_initial_class, form=form_initial_class, extra=0, can_delete=True)
        formset = main_formset(queryset=objects_initial, prefix='object_prefix')


    if validation_mode:
        #THE CODE BELOW DEALS WITH PREPARING DATA FOR VALIDATION MODE OF PAGE VIEWING
        initial_data = dict()
        fields_list = list()
        for object_initial in objects_initial:
            initial_obj = model_to_dict(object_initial)
            for field_name, val in initial_obj.items():
                if not field_name in fields_list:
                    fields_list.append(field_name)

                if val:
                    if type(val).__name__ == "QuerySet":
                        initial_obj[field_name] = {"id": [item.id for item in val], "text": ' '.join([item.name for item in val]) }
            initial_data[initial_obj["id"]] = initial_obj


        deleted_objects = model_update_class.objects.filter(organization=organization, is_marked_deleted=True, is_processed=False)\
            .order_by("-id")
        deleted_objects_list = list()
        deleted_objects_ids = list()
        for item in deleted_objects:
            initial_obj = model_to_dict(item)
            initial_obj_dict = dict()
            for field_name, val in initial_obj.items():
                if field_name in field_name:
                    if val:
                        if type(val).__name__ == "QuerySet":
                            initial_obj_dict[field_name] = ''.join([item.name for item in val])
                        else:
                            initial_obj_dict[field_name] = val
            deleted_objects_list.append(initial_obj_dict)
            deleted_objects_ids.append(initial_obj["id"])

    if request.POST:
        data = request.POST
        print(data)
        if formset:
            print("formset")
            if is_update_objects:
                main_formset = modelformset_factory(model_update_class, form=form_update_class, extra=0, can_delete=True)
                formset = main_formset(request.POST or None, queryset=objects_update, prefix='object_prefix')
            else:
                main_formset = modelformset_factory(model_initial_class, form=form_initial_class, extra=0, can_delete=True)
                formset = main_formset(request.POST or None, queryset=objects_initial, prefix='object_prefix')

            Update.objects.get_or_create(organization=organization, update_status="Unprocessed")
            for formset_form in formset:
                print("formset_form")

                if formset_form.is_valid():
                    print("formset_form is valid")
                    try:
                        if is_update_objects:
                            new_formset_form=formset_form.save(commit=False)
                            new_formset_form.organization = organization
                            new_formset_form.save()
                            formset_form.save_m2m()
                        else:
                            objects_update_is_deleted = model_update_class.objects.filter(organization=organization, is_marked_deleted=True, is_processed=False)
                            objects_update_is_deleted_connection_field = [getattr(item, model_name_initial) for item in objects_update_is_deleted]
                            new_object_update = formset_form.cleaned_data
                            new_object_update["organization"] = organization
                            if "id" in new_object_update and new_object_update["id"] not in objects_update_is_deleted_connection_field:
                                new_object_update[model_name_initial] = new_object_update["id"]#getting program instance in such way
                                new_object_update["id"] = None
                                new_object_update.pop("DELETE")

                                #remake this later into class method
                                #excluding many to many relation fields from the dictionary and applying them after object is created
                                new_object_update_dictionary_for_creation = dict()
                                values_m2m = dict()
                                for field_name, val in new_object_update.items():
                                    if val:
                                        if type(val).__name__ == "QuerySet":
                                            values_m2m[field_name] = val
                                        else:
                                            new_object_update_dictionary_for_creation[field_name] = val

                                new_object = model_update_class.objects.create(**new_object_update_dictionary_for_creation)
                                for field, val in values_m2m.items():
                                    getattr(new_object, field).set(val)

                    except Exception as e:
                        print(e)
                        pass
                else:
                    print(formset_form.errors)
                    print(formset.errors)

            try:
                if is_update_objects:
                    formset.save()
                    for obj in formset.deleted_objects:
                        obj.is_marked_deleted = True
                        obj.save()
            except Exception as e:
                print(e)

            objects_update = model_update_class.objects.filter(organization=organization, is_marked_deleted=False, is_processed=False).order_by("-id")
            main_formset = modelformset_factory(model_update_class, form=form_update_class, extra=0, can_delete=True)
            formset = main_formset(queryset=objects_update, prefix='object_prefix')

    print("pre program")
    #format: model name: related model initial model
    related_objects_mapping = {"Program": "Service",
                               "Service": "Service"
                               }
    if model_initial_class_name == "Program":
        print("program")
        related_model_initial_name = related_objects_mapping[model_initial_class_name]
        related_model_initial_set_name = "%s_set" % related_model_initial_name.lower()

        related_model_update_name = "%sUpdate" % related_objects_mapping[model_initial_class_name]
        related_model_update_set_name = "%supdate_set" % related_model_initial_name.lower()

        #for template
        related_objects_name = "%ss" % (related_model_initial_name.lower())

        base_objects_to_iterate = objects_update if is_update_objects else objects_initial
        related_objects = dict()
        for obj in base_objects_to_iterate:
            print(obj.id)
            if getattr(obj, related_model_update_set_name).all().exists():
                for item in getattr(obj, related_model_update_set_name).all():
                    if not obj.id in related_objects:
                        related_objects[obj.id] = [model_to_dict(item)]
                    else:
                        related_objects[obj.id].append(model_to_dict(item))
            elif getattr(obj, related_model_initial_set_name).all().exists():
                for item in getattr(obj, related_model_initial_set_name).all():
                    if not obj.id in related_objects:
                        related_objects[obj.id] = [model_to_dict(item)]
                    else:
                        related_objects[obj.id].append(model_to_dict(item))

        print(related_objects)

    if validation_mode:
        pending_updates = Update.objects.filter(organization=organization, update_status="Unprocessed").exists()
    return render(request, 'services/editing.html', locals())

