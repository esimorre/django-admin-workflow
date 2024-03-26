

def _create_data(create_su=False, dry_run=False):
    from django_admin_workflow.test.helpers import create_users, create_su as _create_su
    if dry_run:
        print("-------- DRY-RUN ---------")
    print("create users cli1, cli1b (passwd=login) in space Dep1 belonging to the group clients")
    if not dry_run:
        create_users(users=('cli1', 'cli1b'), space="Dep1", group_add='clients')
    print("create users cli2, cli2b (passwd=login) in space Dep2 belonging to the group clients")
    if not dry_run:
        create_users(users=('cli2', 'cli2b'), space="Dep2", group_add='clients')

    if create_su:
        print("create superuser admin/admin")
        if not dry_run: _create_su()

create_data = _create_data