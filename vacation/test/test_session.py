from django_admin_workflow.management.commands.import_workflow import Command as ImportCmd
from django_admin_workflow.test.base import BaseWorkflowTestCase
from vacation.tests import create_data


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

        ob = self.create_workflow_ob()

        rep = self.client.get("/vacation/vacation/")
        l = rep.context_data['cl'].queryset.all()
        rep = self.client.get("/vacation/vacation/add/")
        dfields = rep.context_data['adminform'].fields
        self.assertEqual(len(dfields.keys()) , len(['name', 'contact'] ))
        for key in ['name', 'contact']: self.assertTrue( key in dfields )

        rep = self.client.get("/vacation/vacation/1/change/")
        self.assertEqual( rep.context_data['adminform'].form.initial['name'], '(random) TODO OK')
        self.logout()
