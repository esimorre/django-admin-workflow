from django.contrib.auth.models import Group, User, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

class SpaceManager(models.Manager):
    def get_for_user(self, user):
        return self.get(group__in=user.groups.all())

class Space(models.Model):
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.group:
            self.group , c = Group.objects.get_or_create(name=self.label)
        super().save(force_insert, force_update, using, update_fields)

    label = models.CharField(max_length=40, null=True, blank=True)
    group = models.ForeignKey(Group, null=True, blank=True, related_name='workspaces',
                              verbose_name='groupe associé', on_delete=models.CASCADE,
                              help_text="laisser vide sauf cas spécifique")

    def __str__(self):
        return self.label or self.group.name

    objects = SpaceManager()
    class Meta:
        verbose_name = 'Espace'

class BaseStateModel(models.Model):
    status_choices = (("DRAFT", _("draft")),)
    status = models.SlugField(max_length=8, choices=status_choices, default="DRAFT")
    space = models.ForeignKey(Space, null=True, blank=True, on_delete=models.CASCADE,
                             verbose_name=_("space"))
    creator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("creator"))

    class Meta:
        abstract = True

class NotificationConfig(models.Model):
    space = models.ForeignKey(Space, null=True, blank=True, on_delete=models.CASCADE)
    status = models.CharField(max_length=40, default=_("all"))
    role = models.ForeignKey(Group, null=True, blank=True, related_name='notifier_configs',
                             on_delete=models.CASCADE)

class UserSetting(models.Model):
    user = models.OneToOneField(User, related_name='notif_config', on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    reactive_date = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = _("Settings")


def _get_role_groups():
    return ~Q(name__in=[s.group.name for s in Space.objects.all()])

_ctypes_workfow_pk = []
def _get_workflow_contenttypes(only_ids=False):
    if not _ctypes_workfow_pk:
        for ct in ContentType.objects.all():
            #if ct.model_class() == Status: continue
            if issubclass(ct.model_class(), BaseStateModel):
                _ctypes_workfow_pk.append(ct.pk)
    if only_ids: return _ctypes_workfow_pk
    return Q(pk__in=_ctypes_workfow_pk)

def _get_workflow_permissions():
    ctype_pks = _get_workflow_contenttypes(only_ids=True)
    p = list(Permission.objects.all())
    return (Q(content_type__pk__in=ctype_pks) &
            ~Q(codename__startswith='add_') &
            ~Q(codename__startswith='change_') &
            ~Q(codename__startswith='view_') &
            ~Q(codename__startswith='delete_'))
class Status(models.Model):
    ctype = models.ForeignKey(ContentType, on_delete=models.CASCADE,
                              limit_choices_to=_get_workflow_contenttypes)
    slug = models.SlugField(max_length=8)
    verbose_name = models.CharField(max_length=40)
    bgcolor = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.verbose_name

    class Meta:
        verbose_name = 'Status'
        verbose_name_plural = 'Status values'

class RolePermission(Status):
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert, force_update, using, update_fields)
        Permission.objects.get_or_create(codename=self.slug, name=self.verbose_name,
                                         content_type=self.ctype)

    def groups(self):
        perm = Permission.objects.get(codename=self.slug, name=self.verbose_name,
                                         content_type=self.ctype)
        return " , ".join([g.name for g in Group.objects.filter(permissions=perm)]) or "-"

    def __str__(self):
        return self.verbose_name

    class Meta:
        verbose_name = 'Role'


class ConfigWorkflow(models.Model):
    label = models.CharField(max_length=40, default=_("main"))
    ctype = models.ForeignKey(ContentType, on_delete=models.CASCADE,
                              limit_choices_to=_get_workflow_contenttypes)

    def __str__(self):
        return self.label

    class Meta:
        verbose_name = _('Workflow')

class ConfigRole(models.Model):
    config = models.ForeignKey(ConfigWorkflow, on_delete=models.CASCADE,
                               verbose_name=_("workflow"))
    role = models.ForeignKey(Group, on_delete=models.CASCADE, limit_choices_to=_get_role_groups)
    filter_space = models.BooleanField(default=True)
    filter_user = models.BooleanField(default=False)

    def __str__(self):
        return self.role.name

    class Meta:
        verbose_name = _("Role config")

class ConfigRoleAdd(models.Model):
    config_role = models.OneToOneField(ConfigRole, on_delete=models.CASCADE, related_name='config_add')
    edit_fields = models.CharField(max_length=80, null=True, blank=True)
    readonly_fields = models.CharField(max_length=80, null=True, blank=True)

    def __str__(self):
        return str(self.config_role)

    class Meta:
        verbose_name = _("Role/add config")


class ConfigRoleStatus(models.Model):
    config_role = models.ForeignKey(ConfigRole, on_delete=models.CASCADE, related_name='status_configs')
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE,
                                   limit_choices_to=_get_workflow_permissions)
    edit_fields = models.CharField(max_length=80, null=True, blank=True)
    readonly_fields = models.CharField(max_length=80, null=True, blank=True)

    def workflow_name(self):
        return self.config_role.config.label

    def __str__(self):
        return str(self.config_role) + ':' + str(self.status)

    class Meta:
        verbose_name = _("Role/status config")

class RoleStatusAction(models.Model):
    config_role = models.ForeignKey(ConfigRoleStatus, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=8)
    verbose_name = models.CharField(max_length=40)
    status_change = models.ForeignKey(Status, null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Action"
