from django.db import models


class Language(models.Model):
    code = models.CharField(max_length=5)
    name = models.CharField(max_length=255)

    def __str__(self):
        return "(%s) %s" % (self.code, self.name)


class County(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ('name', )

    def __str__(self):
        return self.name
