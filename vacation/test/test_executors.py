import datetime

from django_admin_workflow.models import Status, SendmailExecutor
from django_admin_workflow.test.base import BaseWorkflowTestCase
from django_admin_workflow.management.commands.import_workflow import Command as ImportCmd
from django_admin_workflow.management.commands.run_executors import Command as ExecCmd
from django.core import mail

from django_admin_workflow.test.helpers import create_obj
from vacation.models import Vacation
from vacation.tests import create_data


class TestCase(BaseWorkflowTestCase):
    @classmethod
    def setUpTestData(cls):
        create_data(create_su=True)
        ImportCmd().handle('vacation/workflow.toml', None)
        create_obj(Vacation, "alba", begin=datetime.date(2024, 8, 1),
                   end=datetime.date(2024, 8, 8), comment="bad request")

    def test0(self):
        self.assertTrue( Status.objects.get(slug="submited") )
        self.assertTrue( Status.objects.get(slug="archived") )

    def test1(self):
        #ExecCmd().handle(executors, models=None, status=None, spaces=None, cron_simul=None)
        ExecCmd().handle(executors=['django_admin_workflow.sendmailexecutor'])
        self.assertEqual( SendmailExecutor.objects.count(), 1)
        exec = SendmailExecutor.objects.first()
        self.assertEqual(exec.running, False)


    def test2(self):
        mail.outbox = []
        self.assertEqual(Vacation.objects.count(), 1)
        ExecCmd().handle(executors=['django_admin_workflow.sendmailexecutor'],
                            models=['vacation.vacation'], status=["DRAFT"])
        self.assertEqual( SendmailExecutor.objects.count(), 1)
        exec = SendmailExecutor.objects.first()
        self.assertEqual(exec.running, False)

        obj = Vacation.objects.first()
        self.assertEqual( obj.status, "sent" )
        self.assertEqual( len(mail.outbox), 1)

        SendmailExecutor._test_simul_failsent = True
        obj.comment = "(simul error sendmail)"
        obj.status = "approved" # status must be registered in workflow.toml, sent is not
        obj.save()
        ExecCmd().handle(executors=['django_admin_workflow.sendmailexecutor'],
                            models=['vacation.vacation'], status=["approved"])
        self.assertEqual( len(mail.outbox), 1)
        obj = Vacation.objects.first()
        self.assertEqual( obj.status, "fail_sent" )


