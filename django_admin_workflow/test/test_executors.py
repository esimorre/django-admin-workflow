from apptest.models import MyTestModel, SendmailExecutor
from django_admin_workflow.models import Status
from django_admin_workflow.test import create_data
from django_admin_workflow.test.base import BaseWorkflowTestCase
from django_admin_workflow.management.commands.import_workflow import Command as ImportCmd
from django_admin_workflow.management.commands.run_executors import Command as ExecCmd
from django_admin_workflow.test.helpers import create_obj


class TestCase(BaseWorkflowTestCase):
    @classmethod
    def setUpTestData(cls):
        create_data(create_su=True)
        ImportCmd().handle('apptest/workflow.toml', None)
        create_obj("test", "cli1")

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
        self.assertEqual(MyTestModel.objects.count(), 1)
        ExecCmd().handle(executors=['apptest.sendmailexecutor'],
                            models=['apptest.mytestmodel'], status=["DRAFT"])
        self.assertEqual( SendmailExecutor.objects.count(), 1)
        exec = SendmailExecutor.objects.first()
        self.assertEqual(exec.running, False)

        obj = MyTestModel.objects.first()
        self.assertEqual( obj.status, "sent" )

        obj.name = "(simul error sendmail)"
        obj.save()
        ExecCmd().handle(executors=['apptest.sendmailexecutor'],
                            models=['apptest.mytestmodel'], status=["sent"])
        obj = MyTestModel.objects.first()
        self.assertEqual( obj.status, "fail_sent" )


