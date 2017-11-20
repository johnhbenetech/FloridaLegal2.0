from django import forms
from .models import *


class ServiceForm(forms.ModelForm):

    class Meta:
        model = Service
        exclude = ["program", "program_update", "organization", "created_by", "created", "modified", "is_edited", "is_marked_deleted"]


class ServiceUpdateForm(forms.ModelForm):

    class Meta:
        model = Service
        exclude = ["organization", "created_by", "created", "modified", "update_status", "is_edited", "is_marked_deleted", "is_processed"]

        widgets = {"service": forms.HiddenInput(),
                   "program": forms.HiddenInput(),
                   "program_update": forms.HiddenInput()
                   }


class ProgramForm(forms.ModelForm):

    class Meta:
        model = Service
        exclude = ["organization", "created_by", "created", "modified"]


class ProgramUpdateForm(forms.ModelForm):

    class Meta:
        model = Service
        exclude = ["organization", "created_by", "created", "modified", "is_edited", "is_marked_deleted", "is_processed"]

        widgets = {'program': forms.HiddenInput()}


class EligibilityForm(forms.ModelForm):

    class Meta:
        model = Eligibility
        exclude = ["service", "service_update",]


class EligibilityUpdateForm(forms.ModelForm):

    class Meta:
        model = EligibilityUpdate
        exclude = ["eligibility", "service", "service_update", "is_marked_deleted", "is_processed"]
