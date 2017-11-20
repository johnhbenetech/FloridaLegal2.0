
from django.contrib.contenttypes.models import ContentType
from django.forms import model_to_dict

class CreationUpdatedInstances(object):
    pass
    foreign_key_fields = ["owner", "organization", "service", "program", "program_update", "service_update"]

    def update_or_create_updated_object_instance(self, update_data=None):
        #it is needed for creation related instances in API calls
        model_class = type(self)
        model_name = model_class.__name__
        connection_field = "%s_id" % model_name.lower()
        model_name_update = "%sUpdate" % model_name

        content_type = ContentType.objects.get(model=model_name_update.lower())
        model_update_class = content_type.model_class()
        based_kwargs = {
            "is_processed": False,
            "is_marked_deleted": False
        }
        kwargs = dict()
        values_m2m = dict()
        obj = model_to_dict(self)
        for field_name, val in obj.items():
            if field_name not in self.exclude_fields_for_update:

                #adding updated fields value from the function parameter
                if update_data and field_name in update_data:
                    val = update_data[field_name]

                if type(val).__name__ == "QuerySet":
                    values_m2m[field_name] = val
                elif field_name == "id":
                    based_kwargs[connection_field] = val
                elif field_name in self.foreign_key_fields:
                    kwargs["%s_id" % field_name] = val
                else:
                    kwargs[field_name] = val
        # print(based_kwargs)
        # print(kwargs)
        update_object, created = model_update_class.objects.update_or_create(**based_kwargs, defaults=kwargs)
        for field, val in values_m2m.items():
            getattr(update_object, field).set(val)

        return update_object