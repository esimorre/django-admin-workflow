from django.contrib.auth.models import Group, User, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

class SpaceManager(models.Manager):
    def get_for_user(self, user):
        if user.is_superuser: return None
        return self.get(group__in=user.groups.all())

class Space(models.Model):
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.group:
            self.group , c = Group.objects.get_or_create(name=self.label)
        super().save(force_insert, force_update, using, update_fields)

    label = models.CharField(max_length=40, null=True, blank=True)
    group = models.ForeignKey(Group, null=True, blank=True, related_name='workspaces',
                              verbose_name=_("linked group"), on_delete=models.CASCADE,
                              help_text="laisser vide sauf cas spécifique")

    def __str__(self):
        return self.label or self.group.name

    objects = SpaceManager()
    class Meta:
        verbose_name = 'Espace'

class BaseStateModel(models.Model):
    status = models.SlugField(max_length=20, default="DRAFT")
    space = models.ForeignKey(Space, null=True, blank=True, on_delete=models.CASCADE,
                             verbose_name=_("space"))
    creator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("creator"))

    def on_before_change_status(self, prev_status):
        """
        Event before saving workflow model. Can be overriden to implement guard

        :prev_status:   previous status
        :return: True for validate saving
        """
        return True

    def on_after_change_status(self, prev_status):
        """
        Event before saving workflow model. Can be overriden to implement automatic activity

        :prev_status:   previous status
        :return: True for validate saving
        """
        pass

    def status_label(self):
        return Status.objects.get(slug=self.status).verbose_name
    status_label.short_description = _("status")

    class Meta:
        abstract = True

class NotificationConfig(models.Model): # TODO
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
def get_workflow_contenttypes(only_ids=False):
    if not _ctypes_workfow_pk:
        for ct in ContentType.objects.all():
            #if ct.model_class() == Status: continue
            cc = ct.model_class()
            if cc and issubclass(cc, BaseStateModel):
                _ctypes_workfow_pk.append(ct.pk)
    if only_ids: return _ctypes_workfow_pk
    return Q(pk__in=_ctypes_workfow_pk)

def get_workflow_permissions():
    ctype_pks = get_workflow_contenttypes(only_ids=True)
    p = list(Permission.objects.all())
    return (Q(content_type__pk__in=ctype_pks) &
            ~Q(codename__startswith='add_') &
            ~Q(codename__startswith='change_') &
            ~Q(codename__startswith='view_') &
            ~Q(codename__startswith='delete_'))

class RoleStatusMixin(models.Model):
    slug = models.SlugField(max_length=20, verbose_name=_("token"))
    verbose_name = models.CharField(max_length=40, verbose_name="label")
    bgcolor = models.CharField(max_length=20, default="LightGray",
                               verbose_name=_("color"),
                               help_text=_("HTML standard color name or #......"))

    def color_display(self):
        tpl = '<span class="button" style="background:%s"> %s </span>'
        return format_html(tpl % (self.bgcolor, self.verbose_name))
    color_display.short_description = _("Label")

    def __str__(self):
        return self.verbose_name
    class Meta:
        abstract = True

class Status(RoleStatusMixin):
    class Meta:
        verbose_name = 'Status'
        verbose_name_plural = 'Status'

class RolePermission(RoleStatusMixin):
    ctype = models.ForeignKey(ContentType, on_delete=models.CASCADE,
                              verbose_name=_("workflow model"),
                              limit_choices_to=get_workflow_contenttypes)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert, force_update, using, update_fields)
        self.get_or_create_permission()

    def get_or_create_permission(self):
        return Permission.objects.get_or_create(codename=self.slug, name=self.verbose_name,
                                         content_type=self.ctype)

    def groups(self):
        perm = Permission.objects.get(codename=self.slug, name=self.verbose_name,
                                         content_type=self.ctype)
        return " , ".join([g.name for g in Group.objects.filter(permissions=perm)]) or "-"

    class Meta:
        verbose_name = 'Role'

class Executor(models.Model):
    status = models.SlugField(max_length=20, help_text=_("status of objects to be processed"))
    space = models.ForeignKey(Space, null=True, blank=True, on_delete=models.CASCADE,
                             verbose_name=_("space"))
    last_run_datetime = models.DateTimeField(null=True, blank=True)
    last_OK = models.BooleanField(default=False)
    running = models.BooleanField(default=False)

    def _start_exec(self):
        if self.running: return False
        self.running = True
        self.last_run_datetime = timezone.now()
        self.save()
        return True

    def _end_exec(self, error=None):
        if error: print("End run on error", error)
        self.last_OK = error == None
        self.running = False
        self.save()

    def run_(self, status, queryset):
        if not self._start_exec(): return
        try:
            nok, msg = self.run(status, queryset)
            error = None
            if nok: error = msg
            self._end_exec(error=error)
        except Exception as e:
            self._end_exec(error=str(e))

    def run(self, status, queryset):
        raise Exception("the run method must be overridden")

    class Meta:
        abstract = True
        verbose_name = _("Executor")
