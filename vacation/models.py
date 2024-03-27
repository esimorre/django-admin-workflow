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

class VacationExecutor(Executor):
    def run(self, status, queryset):
        for obj in queryset.filter(status=status):
            if obj.end < obj.begin or  'bad request' in obj.comment:
                obj.comment = obj.comment + "\nRequest invalid"
                obj.save()

        return 0, "OK"
