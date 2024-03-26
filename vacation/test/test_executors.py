from django_admin_workflow.models import Status, SendmailExecutor
from django_admin_workflow.test.base import BaseWorkflowTestCase
from django_admin_workflow.management.commands.import_workflow import Command as ImportCmd
from django_admin_workflow.management.commands.run_executors import Command as ExecCmd
from django.core import mail

from vacation.models import Vacation
from vacation.tests import create_data


class TestCase(BaseWorkflowTestCase):
    @classmethod
    def setUpTestData(cls):
        create_data(create_su=True)
        ImportCmd().handle('vacation/workflow.toml', None)
        # TODO create_obj("test", "cli1")

    def test0(self):
        self.assertTrue( Status.objects.get(slug="sent") )
        self.assertTrue( Status.objects.get(slug="fail_sent") )

    def test1(self):
        #ExecCmd().handle(executors, models=None, status=None, spaces=None, cron_simul=None)
        ExecCmd().handle(executors=['apptest.sendmailexecutor'])
        self.assertEqual( SendmailExecutor.objects.count(), 1)
        exec = SendmailExecutor.objects.first()
        self.assertEqual(exec.running, False)


    def test2(self):
        mailbox = mail.outbox = []
        self.assertEqual(Vacation.objects.count(), 1)
        ExecCmd().handle(executors=['apptest.sendmailexecutor'],
                            models=['apptest.mytestmodel'], status=["DRAFT"])
        self.assertEqual( SendmailExecutor.objects.count(), 1)
        exec = SendmailExecutor.objects.first()
        self.assertEqual(exec.running, False)

        obj = Vacation.objects.first()
        self.assertEqual( obj.status, "sent" )

        obj.name = "(simul error sendmail)"
        obj.save()
        ExecCmd().handle(executors=['apptest.sendmailexecutor'],
                            models=['apptest.mytestmodel'], status=["sent"])
        self.assertEqual( len(mail.outbox), 2)
        obj = Vacation.objects.first()
        self.assertEqual( obj.status, "fail_sent" )


