from django.db import models

from django_admin_workflow.models import BaseStateModel, Executor, Status


class MyTestModel(BaseStateModel):
    datetime = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100)
    contact = models.EmailField(blank=True, null=True)
    duration = models.DurationField(blank=True, null=True)
    value = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return self.name

class SendmailExecutor(Executor):
    nb_obj_min = 1
    nb_attempts_max = 3
    def run(self, status, queryset=None):
        assert self.status == status or not self.status
        if status and status != [None] and Status.objects.filter(slug__in=status).count() == 0:
            return 1, "Error SendmailExecutor.run: status %s unknown" % status
        if queryset:
            objs = queryset
        else:
            objs = MyTestModel.objects.filter(status__in=status)
        for obj in objs:
            print("process senmail for", obj, "with status", status)
            if "error" in str(obj.name):
                obj.status = 'fail_sent' # simulation fail sendmail for test
            else:
                obj.status = "sent"
            obj.save()
        return 0, "OK"
