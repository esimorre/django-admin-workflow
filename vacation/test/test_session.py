from datetime import datetime, timedelta

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

        rep = self.client.get("/vacation/vacation/")
        l = rep.context_data['cl'].queryset.all()
        rep = self.client.get("/vacation/vacation/add/")
        dfields = rep.context_data['adminform'].fields
        self.assertEqual(len(dfields.keys()) , len(['begin', 'end', 'comment'] ))
        for key in ['begin', 'end', 'comment']: self.assertTrue( key in dfields )

        rep = self.client.get("/vacation/vacation/1/change/")
        self.assertEqual( rep.context_data['adminform'].form.initial['comment'], 'OK')
        self.logout()
