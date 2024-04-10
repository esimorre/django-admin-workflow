from datetime import datetime, timedelta

from django.core import mail

from django_admin_workflow.management.commands.import_workflow import Command as ImportCmd
from django_admin_workflow.test.base import BaseWorkflowTestCase
from ..models import Vacation
from ..tests import create_data


today = datetime.now().date()

class TestCase(BaseWorkflowTestCase):
    @classmethod
    def setUpTestData(cls):
        create_data(create_su=True)
        ImportCmd().handle('vacation/workflow.toml', None)


    def test1(self):
        self.assertAnonymous()
        self.connect("albert")
        rep = self.client.get("/vacation/")
        self.assertAcessApps(rep, ['vacation'])

        ob = self.create_workflow_ob(cls=Vacation, begin=today + timedelta(10),
                                     end=today + timedelta(17), comment="OK")

        rep = self.client.get("/vacation/vacation/add/")
        dfields = rep.context_data['adminform'].fields
        self.assertEqual(len(dfields.keys()) , len(['begin', 'end', 'comment'] ))
        for key in ['begin', 'end', 'comment']: self.assertTrue( key in dfields )

        rep = self.client.get("/vacation/vacation/1/change/")
        self.assertEqual( rep.context_data['adminform'].form.initial['comment'], 'OK')
        self.logout()

    def test_nominal(self):
        """
        test nominal: from DRAFT to archived + notif mail
        """
        # employee creates a vacation request
        self._create_vacation("alba", nb_days=7, comment='8 days', logout=True, submit=True)
        self.assertEqual(Vacation.objects.first().status, "check")

        # auto check
        self.run_auto('vacation.vacationexecutor', "check")
        self.assertEqual(Vacation.objects.first().status, "submited")

        # manager task
        qset = self.read_list("/vacation/vacation/", "claudia", logout=False)
        ob = qset.first()

        # manager approves
        form = self.get_form_data("/vacation/vacation/%d/change/" % ob.pk)
        form['_approve'] = "Approve"
        self.client.post("/vacation/vacation/%d/change/" % ob.pk,form)
        qset = self.read_list("/vacation/vacation/", logout=True)
        self.assertEqual(qset.count(), 0)

        # auto task archives and calculates the balance
        self.run_auto('vacation.vacationexecutor', "approved")
        self.assertEqual(Vacation.objects.first().status, "archived")

        # auto task email notif
        mail.outbox = []
        self.run_auto('vacation.mailexecutor', status="archived")
        mailbox = mail.outbox
        self.assertEqual( len(mail.outbox), 1)
        self.assertTrue("alba" in mailbox[0].to[0])
        self.assertTrue("is accepted" in mailbox[0].body) # request accepted (see mail template)
        self.assertTrue("Your vacation balance is 17 days." in mailbox[0].body) # 25 - 8 = 17 days


    def _create_vacation(self, name, nb_days, comment=None, logout=True, submit=False):
        if not comment: comment = '%s request' % name
        self.connect(name)
        form = {'begin': today, 'end': today + timedelta(days=nb_days),
                         'comment': comment}
        if submit: form['_submit'] = "Submit"
        rep = self.client.post("/vacation/vacation/add/",form)
        if logout: self.logout()


