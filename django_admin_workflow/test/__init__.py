

def create_data():
    from django_admin_workflow.test.helpers import create_space, create_states, create_roles, create_su
    create_space("Dep1", users=('cli1', 'cli1b'), role_add='clients')
    create_space("Dep2", users=('cli2', 'cli2b'), role_add='clients')

    create_states(("accepted", "valid", "published",))
    create_roles(("submiter", "validator", "publisher"))
    create_su()
