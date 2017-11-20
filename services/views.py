from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, HttpResponseRedirect, HttpResponse, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib import messages
from services.models import Service, ServiceUpdate, Program, ProgramUpdate
from .forms import *
from organizations.forms import *
from .models import *
from django.forms.models import modelformset_factory
from organizations.models import Organization
from django.forms import model_to_dict
from organizations.models import Update
from django.contrib.contenttypes.models import ContentType
from django.views.generic import View


class EditingView(View):
    def prepare(self, request, organization_id, page_name, validation_mode, parent_model, parent_obj_id):
        """
        This function prepares shared data both for GET and POST requests.

        It is assumed that page_name has a name of model with "update" word at the end in plural form ("services") starting with a lowcase symbol
        """
        self.organization_id = organization_id
        self.page_name = page_name

        user = request.user
        self.page = page_name

        if validation_mode=="validation_mode":
            self.validation_mode = True
            if not user.is_superuser:
                return HttpResponseRedirect(reverse("home"))
        else:
            self.validation_mode = False


        if user.is_superuser:
            self.organization = get_object_or_404(Organization, id=organization_id)
        else:
            self.organization = get_object_or_404(Organization, id=organization_id, owner=user)

        self.model_name_initial = page_name[:-1].lower()
        content_type = ContentType.objects.get(model=self.model_name_initial.lower())
        self.model_initial_class = content_type.model_class()
        self.model_initial_class_name = self.model_initial_class.__name__
        self.form_initial_name = "%sForm" % self.model_initial_class_name
        self.form_initial_class = globals()[self.form_initial_name]
        self.model_update_class_name = "%sUpdate" % self.model_initial_class_name
        self.model_update_class = globals()[self.model_update_class_name]

        self.form_update_class_name = "%sForm" % self.model_update_class_name
        self.form_update_class = globals()[self.form_update_class_name]

        #Programs formset creation based on Program or ProgramUpdate models
        self.is_update_objects = False
        if not parent_model:
            self.objects_initial = self.model_initial_class.objects.filter(organization=self.organization).order_by("-id")
            #all the programs_update including those one which have pending is_marked_deleted=True
            self.objects_update = self.model_update_class.objects.filter(organization=self.organization, is_processed=False).order_by("id")
        else:
            kwargs = {}
            field_name = "%s_id" % parent_model
            kwargs[field_name] = parent_obj_id
            self.objects_initial = self.model_initial_class.objects.filter(**kwargs).order_by("-id")
            #all the programs_update including those one which have pending is_marked_deleted=True
            kwargs["is_processed"] = False
            self.objects_update = self.model_update_class.objects.filter(**kwargs).order_by("id")


        if self.objects_update:
            self.is_update_objects = True

            #So there are existing programs to update
            # here it is a check if there are any not edited instances of programs
            # and creating ProgramUpdate instances for them
            if self.objects_initial:
                objects_in_update_ids = [getattr(item, self.model_name_initial).id if getattr(item, self.model_name_initial) else None for item in self.objects_update]

                objects_to_add = self.objects_initial.exclude(id__in=objects_in_update_ids).values()
                if objects_to_add:
                    for object_to_add in objects_to_add:
                        fields_to_exclude = ["id", "created", "modified"]
                        fields_to_exclude.append(self.model_name_initial)

                        #maybe to remake this later as a model method
                        update_kwargs = dict()
                        for field_name, val in object_to_add.items():
                            if not field_name in fields_to_exclude:
                                update_kwargs[field_name] = val
                            update_kwargs[self.model_name_initial] = object

                        related_obj = self.model_initial_class.objects.get(id=object_to_add["id"])
                        update_kwargs[self.model_name_initial] = related_obj
                        self.model_update_class.objects.create(**update_kwargs)

            #getting programs_update with the recently added instances + filtering all instances with is_marked_deleted = False
            if not parent_model:
                objects_update = self.model_update_class.objects.filter(organization=self.organization, is_marked_deleted=False, is_processed=False).order_by("id")
            else:
                kwargs = {}
                field_name = "%s_id" % parent_model
                kwargs[field_name] = parent_obj_id
                #all the programs_update including those one which have pending is_marked_deleted=True
                kwargs["is_processed"] = False
                kwargs["is_marked_deleted"] = False
                objects_update = self.model_update_class.objects.filter(**kwargs).order_by("-id")

            main_formset = modelformset_factory(self.model_update_class, form=self.form_update_class, extra=0, can_delete=True)
            self.formset = main_formset(queryset=objects_update, prefix='object_prefix')
        else:
            main_formset = modelformset_factory(self.model_initial_class, form=self.form_initial_class, extra=0, can_delete=True)
            self.formset = main_formset(queryset=self.objects_initial, prefix='object_prefix')


        if validation_mode:
            #THE CODE BELOW DEALS WITH PREPARING DATA FOR VALIDATION MODE OF PAGE VIEWING
            initial_data = dict()
            fields_list = list()
            for object_initial in self.objects_initial:
                initial_obj = model_to_dict(object_initial)
                for field_name, val in initial_obj.items():
                    if not field_name in fields_list:
                        fields_list.append(field_name)

                    if val:
                        if type(val).__name__ == "QuerySet":
                            initial_obj[field_name] = {"id": [item.id for item in val], "text": ' '.join([item.name for item in val]) }
                initial_data[initial_obj["id"]] = initial_obj

            self.initial_data = initial_data

            if not parent_model:
                deleted_objects = self.model_update_class.objects.filter(organization=self.organization, is_marked_deleted=True, is_processed=False).order_by("id")
            else:
                kwargs = {}
                field_name = "%s_id" % parent_model
                kwargs[field_name] = parent_obj_id
                kwargs["is_processed"] = False
                kwargs["is_marked_deleted"] = True
                deleted_objects = self.model_update_class.objects.filter(**kwargs).order_by("id")

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

            self.deleted_objects_list = deleted_objects_list
            self.deleted_objects_ids = deleted_objects_ids

        if self.is_update_objects:
            self.linked_field = self.model_initial_class_name.lower()
        else:
            self.linked_field = None

    def get(self, request, organization_id, page_name, validation_mode=None, parent_model=None, parent_obj_id=None):
        self.prepare(request, organization_id, page_name, validation_mode, parent_model, parent_obj_id)

        #variables assignment for "back" button
        self.organization_id = organization_id
        self.parent_obj_id = parent_obj_id
        self.parent_model = parent_model

        return self.render(request)

    def post(self, request, organization_id, page_name, validation_mode=None, parent_model=None, parent_obj_id=None):

        #variables assignment for "back" button
        self.organization_id = organization_id
        self.parent_obj_id = parent_obj_id
        self.parent_model = parent_model

        data = request.POST
        self.prepare(request, organization_id, page_name, validation_mode, parent_model, parent_obj_id)
        if self.formset:
            if self.is_update_objects:
                main_formset = modelformset_factory(self.model_update_class, form=self.form_update_class, extra=0, can_delete=True)
                self.formset = main_formset(request.POST or None, queryset=self.objects_update, prefix='object_prefix')
            else:
                main_formset = modelformset_factory(self.model_initial_class, form=self.form_initial_class, extra=0, can_delete=True)
                self.formset = main_formset(request.POST or None, queryset=self.objects_initial, prefix='object_prefix')

            Update.objects.get_or_create(organization=self.organization, update_status="Unprocessed")
            for formset_form in self.formset:

                if formset_form.is_valid():
                    try:
                        if self.is_update_objects:
                            new_formset_form=formset_form.save(commit=False)
                            if not parent_model:
                                new_formset_form.organization = self.organization
                            else:
                                field_name = "%s_id" % parent_model
                                setattr(new_formset_form, field_name, parent_obj_id)
                            new_formset_form.save()
                            formset_form.save_m2m()
                        else:
                            if not parent_model:
                                objects_update_is_deleted = self.model_update_class.objects.filter(organization=self.organization, is_marked_deleted=True, is_processed=False).order_by("id")
                            else:
                                kwargs = {}
                                field_name = "%s_id" % parent_model
                                kwargs[field_name] = parent_obj_id
                                kwargs["is_marked_deleted"] = True
                                kwargs["is_processed"] = False
                                objects_update_is_deleted = self.model_update_class.objects.filter(**kwargs).order_by("id")

                            objects_update_is_deleted_connection_field = [getattr(item, self.model_name_initial) for item in objects_update_is_deleted]
                            new_object_update = formset_form.cleaned_data

                            if not parent_model:
                                new_object_update["organization"] = self.organization
                            if "id" in new_object_update and new_object_update["id"] not in objects_update_is_deleted_connection_field:
                                new_object_update[self.model_name_initial] = new_object_update["id"]#getting program instance in such way
                                new_object_update["id"] = None
                                new_object_update.pop("DELETE")

                                if parent_model:
                                    content_type = ContentType.objects.get(model=parent_model.replace("_","").lower())
                                    parent_model_class = content_type.model_class()
                                    parent_model_obj = parent_model_class.objects.get(id=parent_obj_id)
                                    new_object_update[parent_model] = parent_model_obj

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

                                new_object = self.model_update_class.objects.create(**new_object_update_dictionary_for_creation)
                                for field, val in values_m2m.items():
                                    getattr(new_object, field).set(val)

                    except Exception as e:
                        print(e)
                        pass

            try:
                if self.is_update_objects:
                    self.formset.save()
                    for obj in self.formset.deleted_objects:
                        obj.is_marked_deleted = True
                        obj.save()
            except Exception as e:
                print(e)


            if not parent_model:
                self.objects_update = self.model_update_class.objects.filter(organization=self.organization, is_marked_deleted=False, is_processed=False).order_by("id")
            else:
                kwargs = {}
                field_name = "%s_id" % parent_model
                kwargs[field_name] = parent_obj_id
                kwargs["is_marked_deleted"] = False
                kwargs["is_processed"] = False
                self.objects_update = self.model_update_class.objects.filter(**kwargs).order_by("id")

            #Put self.is_update_objects True because now "Update" model instances will be displayed on a template
            self.is_update_objects = True

            self.main_formset = modelformset_factory(self.model_update_class, form=self.form_update_class, extra=0, can_delete=True)
            self.formset = main_formset(queryset=self.objects_update, prefix='object_prefix')

            return self.render(request)

    def render(self, request):
        #format: model name: related model initial model
        self.getting_related_objects()
        self.getting_pending_update()
        self.get_previous_url()

        return render(request, 'services/editing.html', {
            "organization": self.organization,
            "organization_id": self.organization_id,
            "validation_mode": self.validation_mode,
            "pending_updates": self.pending_updates,
            "related_objects": self.related_objects,
            "related_objects_name": self.related_objects_name,
            "formset": self.formset,
            "currently_edited_model": self.currently_edited_model_name,
            "page": self.page,
            "initial_data": self.initial_data if self.validation_mode == True else None,
            "previous_url": self.previous_url,
            "linked_field": self.linked_field,
            "related_objects_ids": self.related_objects_ids
        })

    def getting_pending_update(self):
        if self.validation_mode:
            self.pending_updates = Update.objects.filter(organization=self.organization, update_status="Unprocessed").exists()
        else:
            self.pending_updates = None


    def getting_related_objects(self):
        related_objects_mapping = {"Program": "Service",
                                   "Service": "Eligibility"
                                   }

        self.related_objects_ids = list()
        if self.model_initial_class_name in related_objects_mapping:
            related_model_initial_name = related_objects_mapping[self.model_initial_class_name]
            related_model_initial_set_name = "%s_set" % related_model_initial_name.lower()

            related_model_update_name = "%sUpdate" % related_objects_mapping[self.model_initial_class_name]
            related_model_update_set_name = "%s_set" % related_model_update_name.lower()

            #for template
            self.related_objects_name = "%ss" % (related_model_initial_name.lower())

            #for url in template
            if self.is_update_objects:
                self.currently_edited_model_name = "%s_update" % self.model_initial_class_name.lower()
            else:
                self.currently_edited_model_name = "%s" % self.model_initial_class_name.lower()


            base_objects_to_iterate = self.objects_update if self.is_update_objects else self.objects_initial
            related_objects = dict()
            for obj in base_objects_to_iterate:

                if getattr(obj, related_model_update_set_name).all().exists():

                    #this is needed for check on templates to show Related objects add button, when there are now related objects
                    self.related_objects_ids.append(obj.id)

                    for item in getattr(obj, related_model_update_set_name).all():
                        if not obj.id in related_objects:
                            related_objects[obj.id] = [model_to_dict(item)]
                        else:
                            related_objects[obj.id].append(model_to_dict(item))
                elif getattr(obj, related_model_initial_set_name).all().exists():

                    #this is needed for check on templates to show Related objects add button, when there are now related objects
                    self.related_objects_ids.append(obj.id)

                    for item in getattr(obj, related_model_initial_set_name).all():
                        if not obj.id in related_objects:
                            related_objects[obj.id] = [model_to_dict(item)]
                        else:
                            related_objects[obj.id].append(model_to_dict(item))
            self.related_objects = related_objects
        else:
            self.related_objects = None
            self.related_objects_name = None
            self.currently_edited_model_name = None


    def get_previous_url(self):
        self.previous_url = None
        if self.model_initial_class_name == "Service":
            kwargs = {
                "organization_id": self.organization_id,
                "page_name": "programs"
            }
            if self.validation_mode:
                kwargs["validation_mode"] = "validation_mode"
                self.previous_url = reverse("editing_validation", kwargs=kwargs)
            else:
                self.previous_url = reverse("editing", kwargs=kwargs)

        if self.model_initial_class_name == "Eligibility":
            content_type = ContentType.objects.get(model=self.parent_model.replace("_","").lower())
            parent_model_class = content_type.model_class()
            parent_model_obj = parent_model_class.objects.get(id=self.parent_obj_id)
            service = parent_model_obj
            if service.program_update:
                parent_obj_id = service.program_update.id
                parent_model = "program_update"
            else:
                parent_obj_id = service.program.id
                parent_model = "program"

            kwargs = {
                "organization_id": self.organization_id,
                "page_name": "services",
                "parent_model": parent_model,
                "parent_obj_id": parent_obj_id

            }
            if self.validation_mode:
                kwargs["validation_mode"] = "validation_mode"
                self.previous_url = reverse("editing_related_objects_validation", kwargs=kwargs)
            else:
                self.previous_url = reverse("editing_related_objects", kwargs=kwargs)