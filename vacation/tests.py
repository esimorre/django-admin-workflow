from django_admin_workflow.management.commands.import_workflow import Command as ImportCmd

from django_admin_workflow.test.base import BaseWorkflowTestCase


def create_data(create_su=False, dry_run=False):
    from django_admin_workflow.test.helpers import create_users, create_su as _create_su
    if dry_run:
        print("-------- DRY-RUN ---------")
    print("create users albert, felix (passwd=login) in space french branch belonging to the group employees")
    if not dry_run:
        create_users(users=('albert', 'felix'), space="french branch", group_add='employees')

    print("create users alba, sara (passwd=login) in space spain branch belonging to the group employees")
    if not dry_run:
        create_users(users=('alba', 'sara'), space="spain branch", group_add='employees')

    print("create users bob, claudia (passwd=login) belonging to the group managers")
    if not dry_run:
        create_users(users=('bob',), space="french branch", group_add='managers')
        create_users(users=('claudia',), space="spain branch", group_add='managers')

    if create_su:
        print("create superuser admin/admin")
        if not dry_run: _create_su()

class TestCase(BaseWorkflowTestCase):
    @classmethod
    def setUpTestData(cls):
        create_data(create_su=True)
        ImportCmd().handle('vacation/workflow.toml', None)

    def test1(self):
        pass
