from django_admin_workflow.management.commands.import_workflow import Command as ImportCmd
from . import create_data
from .base import BaseWorkflowTestCase


class TestCase(BaseWorkflowTestCase):
    @classmethod
    def setUpTestData(cls):
        create_data(create_su=True)
        ImportCmd().handle('apptest/workflow.toml', None)


    def test1(self):
        self.assertAnonymous()
        self.connect("cli1")
        rep = self.client.get("/apptest/")
        self.assertAcessApps(rep, ['apptest'])

        ob = self.create_workflow_ob()

        rep = self.client.get("/apptest/mytestmodel/")
        l = rep.context_data['cl'].queryset.all()
        rep = self.client.get("/apptest/mytestmodel/add/")
        dfields = rep.context_data['adminform'].fields
        self.assertEqual(len(dfields.keys()) , len(['name', 'contact'] ))
        for key in ['name', 'contact']: self.assertTrue( key in dfields )

        rep = self.client.get("/apptest/mytestmodel/1/change/")
        self.assertEqual( rep.context_data['adminform'].form.initial['name'], '(random) TODO OK')
        self.logout()
