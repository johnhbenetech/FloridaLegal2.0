from organizations.models import Organization, STATUS_CHOICES


def default_context(request):
    user = request.user
    return_dict = dict()
    if not user.is_anonymous:
        if user.is_superuser:
            return_dict["available_organizations"] = Organization.objects.all()
        else:
            return_dict["available_organizations"] = Organization.objects.filter(owner=user)

        return_dict["statuses"] = STATUS_CHOICES

    return return_dict