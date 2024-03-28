from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType

from django_admin_workflow.test.base import BaseWorkflowTestCase
from django_admin_workflow.test.helpers import create_users
from vacation.models import Vacation


class BasicTestCase(BaseWorkflowTestCase):
    @classmethod
    def setUpTestData(cls):
        create_users(users=('cli1', 'cli1b'), space="Dep1", group_add='clients')
        create_users(users=('cli2', 'cli2b'), space="Dep2", group_add='clients')

    def test1_init(self):
        self.assertEqual(User.objects.get(username='cli1').groups.all()[0].name, 'Dep1')
        self.assertEqual(User.objects.get(username='cli1').groups.all()[1].name, 'clients')


    def test2_add_perms(self):
        ct = ContentType.objects.get_for_model(Vacation)
        users = User.objects.all()
        p = Permission.objects.get_by_natural_key(codename="add_vacation",
                                                  app_label="vacation", model="vacation")
        users[0].user_permissions.set([p])
        p = Permission.objects.create(codename="can_edit", name="Can Edit", content_type=ct)
        users[0].user_permissions.add(p)
        clients = users[0].groups.all()[1]
