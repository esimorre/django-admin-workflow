from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase

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

    def create_workflow_ob(self, cls, **kwargs):
        print("  +++ create ob ", cls, "attrs", kwargs)
        ob = cls.objects.create(creator=self._user, space=Space.objects.get_for_user(self._user),
                                        **kwargs)
        self.assertEqual(ob.status, 'DRAFT')
        return ob

    def assertAcessApps(self, rep, apps):
        self.assertEqual(rep.status_code, 200)
        self.assertEqual( len(rep.context_data['app_list']), len(apps))
        self.assertEqual( rep.context_data['app_label'], apps[0])
