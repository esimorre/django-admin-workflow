from django.contrib.auth.models import User, Group

from django_admin_workflow.models import Space


def create_partition(name, users, role_add=False):
    Space.objects.create(label=name)
    for u in users:
        obu = User.objects.create_user(u, password=u)
        obu.groups.add(Group.objects.get(name=name))
        if role_add:
            g, c = Group.objects.get_or_create(name=role_add)
            obu.groups.add(g)