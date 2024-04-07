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
    def run(self, status_list, queryset):
        if status_list and status_list != [None]:
            q = queryset.filter(statu__in=status_list)
        else:
            q = queryset.all()
        if q.count() > 0:
            return self._check(q)
        return 0, "OK"

    def _check(self, q):
        for obj in q:
            if obj.status != "check": continue
            delta = obj.end - obj.begin
            if delta.days < 0 or  'bad request' in obj.comment:
                obj.comment = obj.comment + "\nRequest invalid"
                obj.status = "DRAFT"
                obj.save()
                continue
            account = UserAccount.objects.get(user=obj.creator)
            if delta.days + 1 > account.provision:
                obj.comment = obj.comment + "\nInsufficient provision"
                obj.status = "DRAFT"
                obj.save()
                continue
            # OK to submited
            obj.status = "submited"
            obj.save()
        return 0, "OK"


# override create_data for command add_sample
import django_admin_workflow.test
from .tests import create_data
django_admin_workflow.test.create_data = create_data
