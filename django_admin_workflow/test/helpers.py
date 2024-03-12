from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType

from django_admin_workflow.models import Space, Status, RolePermission

def create_su():
    return User.objects.create_superuser("admin", "admin@test.fr", "admin")
def create_space(name, users, role_add=None):
    """
    create a space with users belonging to it.
    :name:  space name
    :users: usernames
    :role_add: group name allowing to add objects (default None)
    """
    Space.objects.create(label=name)
    for u in users:
        obu = User.objects.create_user(u, password=u)
        obu.groups.add(Group.objects.get(name=name))
        if role_add:
            g, c = Group.objects.get_or_create(name=role_add)
            obu.groups.add(g)

def create_states(slugs, app_label="apptest", model_name="mytestmodel", cls=Status):
    ct = ContentType.objects.get_by_natural_key(app_label, model_name)
    for slug in slugs:
        verb = slug[0].capitalize() + slug[1:]
        cls.objects.get_or_create(ctype=ct, slug=slug,
                                     defaults={"verbose_name": verb})

def create_roles(slugs, app_label="apptest", model_name="mytestmodel"):
    create_states(slugs, app_label, model_name, cls=RolePermission)