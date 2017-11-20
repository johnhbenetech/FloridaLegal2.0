from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token


def user_post_save(sender, instance,  created, **kwargs):
    print("user post save")
    if created:
        user = instance

        #creation of API token for a new user
        Token.objects.create(user=user)

post_save.connect(user_post_save, sender=User)
