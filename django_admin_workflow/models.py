from django.contrib.auth.models import Group, User, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from django.db import models
from django.db.models import Q
from django.template import loader
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

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("admin:%s_%s_change" % (self._meta.app_label, self._meta.model_name),
                       args=[self.pk])

    def status_label(self):
        return Status.objects.get(slug=self.status).verbose_name
    status_label.short_description = _("status")

    class Meta:
        abstract = True

class NotificationConfigManager(models.Manager):
    def get_users_to_notify(self):
        pass # TODO
class NotificationConfig(models.Model): # TODO
    space = models.ForeignKey(Space, null=True, blank=True, on_delete=models.CASCADE)
    status = models.CharField(max_length=40, default="all")
    role = models.ForeignKey(Group, null=True, blank=True, related_name='notifier_configs',
                             on_delete=models.CASCADE)
    email_active = models.BooleanField(default=True)
    objects = NotificationConfigManager()


class UserSetting(models.Model):
    user = models.OneToOneField(User, related_name='notif_config',
                                editable=False, on_delete=models.CASCADE)
    email_active = models.BooleanField(default=True, verbose_name=_("email notification active"))
    reactive_date = models.DateField(null=True, blank=True, verbose_name=_("reactivation date"))

    def link_field(self):
        return _("Notifications")
    link_field.short_description = _("my settings")
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("admin:django_admin_workflow_usersetting_change", args=[self.pk])

    def __str__(self):
        return _("%s's settings") % self.user.username

    class Meta:
        verbose_name = _("Settings")
        verbose_name_plural = _("Settings")


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

class SendmailExecutor(Executor):
    nb_obj_min = 1
    nb_attempts_max = 3
    def run(self, status, queryset=None):
        assert self.status == status or not self.status

        global_settings, _ = NotificationConfig.objects.get_or_create()
        if not global_settings.email_active:
            return 0, "email notification not active" # TODO

        if status and status != [None] and Status.objects.filter(slug__in=status).count() == 0:
            return 1, "Error SendmailExecutor.run: status %s unknown" % status
        if queryset:
            objs = queryset
        else:
            # objs = MyTestModel.objects.filter(status__in=status)
            # TODO
            raise Exception("NYI")

        for obj in objs:
            print("process senmail for", obj, "with status", status)

            # settings
            # user settings TODO
            usettings, _ = UserSetting.objects.get_or_create(user=obj.creator)
            if not usettings.email_active: continue

            app_label = self._meta.app_label
            template = loader.select_template(['%s/mail/notif_%s.txt' % (app_label, obj.status),
                                               '%s/mail/notif.txt' % app_label,
                                               'django_admin_workflow/mail/notif.txt'])
            context = {
                'obj': obj,
                'status': status,
                'user': obj.creator.first_name or obj.creator.username,
                'settings_link': obj.creator.notif_config.get_absolute_url()
            }

            cr = send_mail(
                "Subject here",
                template.render(context=context),
                "from@example.com",
                [obj.creator.email],
                fail_silently=False,
            )

            if "error" in str(obj.comment):
                obj.status = 'fail_sent' # simulation fail sendmail for test
            else:
                obj.status = "sent"
            obj.save()
        return 0, "OK"
