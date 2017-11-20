from rest_framework import serializers
from organizations.models import *
from services.models import *


class EligibilitySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    class Meta:
        model = Eligibility
        fields = '__all__'


class EligibilityUpdateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    class Meta:
        model = EligibilityUpdate
        fields = '__all__'


class ServiceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    eligibility = EligibilitySerializer(source='eligibility_set', many=True)
    class Meta:
        model = Service
        fields = '__all__'


class ServiceUpdateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    eligibility_update = EligibilityUpdateSerializer(source='eligibilityupdate_set', many=True)
    class Meta:
        model = ServiceUpdate
        fields = '__all__'


class ProgramSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    services = ServiceSerializer(source='service_set', many=True)
    class Meta:
        model = Program
        fields = '__all__'


class ProgramUpdateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    services_update = ServiceUpdateSerializer(source='serviceupdate_set', many=True)
    class Meta:
        model = ProgramUpdate
        fields = '__all__'


class LocationSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    class Meta:
        model = Location
        fields = '__all__'


class LocationUpdateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    class Meta:
        model = LocationUpdate
        fields = '__all__'


class UpdatingLogic(object):
    pass

    def update(self, instance, validated_data):
        if not "organization" in validated_data:
            organization_initial = Organization.objects.get(id=instance.id)
            self.organization = organization_initial
        else:
            organization = validated_data["organization"]
            organization_initial = organization
            self.organization = organization_initial

        organization_update = organization_initial.update_or_create_updated_object_instance(update_data=validated_data)
        Update.objects.get_or_create(organization=organization_initial, update_status="Unprocessed")


        #organization instances will be updated automatically
        #so here is the logic for updating only related objects
        instance_data = validated_data

        related_objects = ["location_set", "program_set", "locationupdate_set", "programupdate_set"]
        for instance_name in related_objects:
            if instance_name in instance_data:
                related_instances_data = instance_data[instance_name]
                for related_instance_data in related_instances_data:
                    self.custom_update_objects(instance_name, related_instance_data,
                                               parent_instance_name="organization_update",
                                               parent_instance_id=organization_update.id)



        return instance


    def preparing_object_for_creation_or_updating(self, objects_dict):
        m2m_fields = dict()
        obj_fields = dict()
        related_objects_dict = dict()
        for k, v in objects_dict.items():
            if k.endswith("_set"):
                related_objects_dict[k] = v
            elif type(v) is list:
                m2m_fields[k] = v
            elif k != "id":
                obj_fields[k] = v
        return (m2m_fields, obj_fields, related_objects_dict)

    def populate_remaining_update_instances(self):
        organization = self.organization
        self.locations = Location.objects
        self.related_models = {"Program": ["Service"], "Service": ["Eligibility"]}
        self.mapping = {"Location": "organization", "Program": "organization", "Service": "program", "Eligibility": "service"}
        self.mapping_data = {"organization": organization}
        models = ["Location", "Program"]
        for model in models:
            self.populating_data(model)


    def populating_data(self, model):
        model_initial_class = globals()[model]
        model_update_name = "%sUpdate" % model
        model_update_class = globals()[model_update_name]

        connection_field = "%s_id" % model.lower()
        kwargs = dict()
        kwargs_update_model = dict()
        field = self.mapping[model]
        kwargs[field] = self.mapping_data[field]
        kwargs_update_model["%s__isnull" % connection_field] = True
        kwargs_update_model["is_processed"] = False
        kwargs_update_model["is_marked_deleted"] = False
        model_update_objects = model_update_class.objects.filter(**kwargs_update_model)
        model_update_objects_connection_field_ids = [getattr(item, connection_field) for item in model_update_objects]

        model_initial_objects = model_initial_class.objects.filter(**kwargs)
        if model_initial_objects:
            for obj in model_initial_objects:
                if not obj.id in model_update_objects_connection_field_ids:
                    obj.update_or_create_updated_object_instance()

                    if not model.lower() in self.mapping_data:
                        self.mapping_data[model.lower()] = obj
                        related_models = self.related_models.get(model)
                        if related_models:
                            for related_model in related_models:
                                self.populating_data(related_model)


    def custom_update_objects(self, instance_name, instance_data, parent_instance_name=None, parent_instance_id=None):
        #logic of related objects
        if instance_name in instance_data:
            instance_data.pop(instance_name)#delete organization from sent data to prevent hacking
        item_id = instance_data.get("id")
        initial_is_updated = None
        if instance_name.endswith("_set"):
            if instance_name.endswith("update_set"):
                initial_instance = "%sUpdate" % instance_name.split("update_set")[0].capitalize()
                updated_instance_name = "%s_update" % instance_name.split("update_set")[0] #field name
                initial_is_updated = True
            else:
                initial_instance = instance_name.split("_set")[0].capitalize()
                updated_instance_name = "%s_update" % instance_name.split("_set")[0] #field name
        else:
            if instance_name.endswith("update_set"):
                initial_instance = "%sUpdate" % instance_name.split("update")[0].capitalize()
                updated_instance_name = "%s_update" % instance_name.split("update")[0]
                initial_is_updated = True
            else:
                initial_instance = instance_name.capitalize()
                updated_instance_name = "%s_update" % instance_name

        initial_instance_model_class = globals()[initial_instance]

        if initial_is_updated:
            updated_instance_model_class = initial_instance_model_class
        else:
            updated_instance = "%sUpdate" % initial_instance
            updated_instance_model_class = globals()[updated_instance]

        #if existing item
        if item_id:
            #updating instance
            if initial_is_updated:
                obj = initial_instance_model_class.objects.get(id=item_id)
            else:
                obj_initial = initial_instance_model_class.objects.get(id=item_id)

                #1st step - create related Update object
                obj = obj_initial.update_or_create_updated_object_instance()

            #2nd step - update it with new data
            m2m_fields, obj_fields, related_objects_dict = self.preparing_object_for_creation_or_updating(
                objects_dict=instance_data)
            for k, v in obj_fields.items():
                setattr(obj, k, v)
            obj.save()
            for field, val in m2m_fields.items():
                getattr(obj, field).set(val)

            if related_objects_dict:
                for related_instance_name, related_instance_items in related_objects_dict.items():
                    for related_instance_item in related_instance_items:
                        self.custom_update_objects(related_instance_name, related_instance_item,
                                                   parent_instance_name=updated_instance_name, parent_instance_id=obj.id)
        else:
            #creating instance
            m2m_fields, obj_fields, related_objects_dict = self.preparing_object_for_creation_or_updating(objects_dict=instance_data)

            if instance_name in ["program_set", "location_set"]:
                obj_fields["organization"] = self.organization

            if instance_name in ["service_set", "serviceupdate_set", "eligibility_set", "eligibilityupdate_set"]:
                parent_instance_field = "%s_id" % parent_instance_name
                obj_fields[parent_instance_field] = parent_instance_id

            obj = updated_instance_model_class.objects.create(**obj_fields)
            for field, val in m2m_fields.items():
                getattr(obj, field).set(val)

            if related_objects_dict:
                for related_instance_name, related_instance_items in related_objects_dict.items():
                    for related_instance_item in related_instance_items:
                        self.custom_update_objects(related_instance_name, related_instance_item,
                                                   parent_instance_name=updated_instance_name, parent_instance_id=obj.id)

        self.populate_remaining_update_instances()
        return True


class OrganizationSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    programs = ProgramSerializer(source='program_set', many=True, required=False)
    locations = LocationSerializer(source='location_set', many=True, required=False)

    class Meta:
        model = Organization
        fields = '__all__'

    def update(self, instance, validated_data):
        return UpdatingLogic().update(instance, validated_data)



class OrganizationUpdateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    programs_update = ProgramUpdateSerializer(source='programupdate_set', many=True, required=False, read_only=True)
    locations_update = LocationUpdateSerializer(source='locationupdate_set', many=True, required=False, read_only=True)

    class Meta:
        model = OrganizationUpdate
        fields = '__all__'

    def update(self, instance, validated_data):
        return UpdatingLogic().update(instance, validated_data)