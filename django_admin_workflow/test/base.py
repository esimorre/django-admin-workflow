from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase

from apptest.models import MyTestModel
from django_admin_workflow.models import Space


class BaseWorkflowTestCase(TestCase):

    def assertAnonymous(self, path='/'):
        self.assertEqual(self.client.get(path).status_code, 302)
        print("\n>> non connected")

    def connect(self, name, passwd=None):
        if not passwd: passwd = name
        rep = self.client.post("/login/", {"username": name, "password": passwd})
        self.assertEqual(rep.status_code, 302)
        self.assertEqual(self.client.get("/").status_code, 200)
        print("\n>> connected as", name)
        self._user = User.objects.get(username=name)

    def logout(self):
        print(">> logout")
        self.client.logout()
        self.assertAnonymous()

    def create_workflow_ob(self, type='OK', value=None):
        print("  +++ create ob type", type, "value", value or '(random)')
        if not value: value = '(random) TODO '
        ob = MyTestModel.objects.create(creator=self._user, space=Space.objects.get_for_user(self._user),
                                        name=value + type, duration=timedelta(seconds=101))
        self.assertEqual(ob.status, 'DRAFT')
        print(ob.name, ob.duration)
        return ob

    def assertAcessApps(self, rep, apps):
        self.assertEqual(rep.status_code, 200)
        self.assertEqual( len(rep.context_data['app_list']), len(apps))
        self.assertEqual( rep.context_data['app_label'], apps[0])
