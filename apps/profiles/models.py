from django.db import models
from django.contrib.auth.models import User
from tagging.fields import TagField
from tagging.models import Tag
from tagging_autocomplete.models import TagAutocompleteField

class Profile(models.Model):
    user = models.OneToOneField(User)
    def __unicode__(self):
        return unicode(self.user)

class Skill(models.Model):
    name = models.CharField(max_length=50)
    profiles = models.ManyToManyField(Profile)
    def __unicode__(self):
        return self.name
