

def create_data():
    from django_admin_workflow.test.helpers import create_users, create_states, create_roles, create_su
    create_users(users=('cli1', 'cli1b'), space="Dep1", group_add='clients')
    create_users(users=('cli2', 'cli2b'), space="Dep2", group_add='clients')

    create_states(("accepted", "valid", "published",))
    create_roles(("submiter", "validator", "publisher"))
    create_su()
