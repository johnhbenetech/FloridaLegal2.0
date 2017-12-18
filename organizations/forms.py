from django import forms
from .models import *


class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        exclude = ["owner", "created_by", "created", "modified"]


class OrganizationUpdateForm(forms.ModelForm):
    class Meta:
        model = OrganizationUpdate
        exclude = ["owner", "created_by", "created", "modified", "organization", "validation_note", "update_status",
                   "is_marked_deleted", "is_processed"]

        widgets = {"organization": forms.HiddenInput()}


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        exclude = ["organization","latitude","longitude"]


class LocationUpdateForm(forms.ModelForm):
    class Meta:
        model = Location
        exclude = ["organization", "created_by", "is_processed", "is_marked_deleted","latitude","longitude"]

        widgets = {"location": forms.HiddenInput()}


class UpdateForm(forms.ModelForm):
    class Meta:
        model = Update
        exclude = ["organization", "created", "modified"]