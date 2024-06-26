from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models, transaction

from django_admin_workflow.models import BaseStateModel, Executor, SendmailExecutor
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
        if queryset.count() > 0:
            if not status or status == "check":
                self._check(queryset.filter(status="check"))
            if not status or status == "approved":
                self._archive(queryset.filter(status="approved"))

        return 0, "OK"

    def _check(self, q):
        for obj in q:
            if obj.status != "check": continue
            delta = obj.end - obj.begin
            if delta.days < 0 or  'bad request' in obj.comment:
                obj.comment = obj.comment + "\nRequest invalid"
                self.save_state(obj, "DRAFT")
                continue
            account = UserAccount.objects.get(user=obj.creator)
            if delta.days + 1 > account.provision:
                obj.comment = obj.comment + "\nInsufficient provision"
                self.save_state(obj, "DRAFT")
                continue
            # OK to submited
            self.save_state(obj, "submited")

    def _archive(self, q):
        for obj in q:
            if obj.status != "approved": continue
            delta = obj.end - obj.begin
            with transaction.atomic():
                account = UserAccount.objects.get(user=obj.creator)
                account.provision -= (delta.days + 1)
                account.save()
                self.save_state(obj, "archived")

class MailExecutor(SendmailExecutor):
    """
    Template used is vacation/mail/notif_archived.txt
    the executor command should be
        python manage.py run_executors -e vacation.mailexecutor -s archived
    """
    sent_status = 'archived' # status unchanged
    def get_extra_context(self, obj):
        return {'provision': obj.creator.vacations.first().provision}


# override create_data for command add_sample
import django_admin_workflow.test
from .tests import create_data
django_admin_workflow.test.create_data = create_data
