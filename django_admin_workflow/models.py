from django.contrib.auth.models import Group
from django.db import models


class Status(models.TextChoices):
    DRAFT   = "d", "Draft"
    PUBLISH = "p", "Published"


class BaseStateModel(models.Model):
    status = models.CharField(max_length=1, choices=Status, default=Status.DRAFT)
    space = models.CharField(max_length=40, default='default', editable=False)
    creator = models.CharField(max_length=40, default='admin', editable=False)

    class Meta:
        abstract = True
        permissions = [("can_edit", "Editor role"),
                       ("can_publish", "Publisher role"),]

class SpaceManager(models.Manager):
    def user_space_groupname(self, user):
        names = [space.group.name for space in self.all()]
        return user.groups.get(name__in=names)

    def get_for_user(self, user):
        return self.get(group__in=user.groups)

class Space(models.Model):
    label = models.CharField(max_length=40, null=True, blank=True)
    group = models.ForeignKey(Group, null=True, blank=True, related_name='workspaces', verbose_name='groupe associé',
                              on_delete=models.CASCADE)

    def __str__(self):
        return self.label or self.group.name

    objects = SpaceManager()
    class Meta:
        verbose_name = 'Partitionnement'
