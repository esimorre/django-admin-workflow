from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models

from django_admin_workflow.models import BaseStateModel, Executor
from django.utils.translation import gettext_lazy as _



class Vacation(BaseStateModel):
    begin = models.DateField(verbose_name=_("start"))
    end = models.DateField()
    comment = models.TextField(max_length=100)

    def duration(self):
        return (self.end - self.begin).days + 1
    duration.short_description = _("duration (days)")

class UserAccount(models.Model):
    user = models.ForeignKey(User, related_name='vacations', on_delete=models.CASCADE)
    provision = models.PositiveIntegerField()

import django_admin_workflow.test
from .tests import create_data
django_admin_workflow.test.create_data = create_data

class VacationExecutor(Executor):
    def run(self, status, queryset):
        return 1, "not yet implemented"
