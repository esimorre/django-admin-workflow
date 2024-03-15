from django.contrib import admin, messages
from django.contrib.admin.models import LogEntry
from django.utils.html import format_html

from .models import Space, Status, RolePermission
from django.utils.translation import gettext_lazy as _


@admin.register(Space)
class SpaceAdmin(admin.ModelAdmin):
    pass

@admin.register(LogEntry)
class LogEntry(admin.ModelAdmin):
    list_display = ('action_time', 'user', 'object_repr', '__str__')
    date_hierarchy = 'action_time'
    list_filter = ('user',)
    search_fields = ('object_repr',)
    search_help_text = "nom d'objet"


# Gestionnaire des vues admin respectant les règles groupe/permissions/champs exposés
class WorkflowModelAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        list_display = list(super().get_list_display(request))
        if not request.user.is_superuser:
            if 'space' in list_display: list_display.remove('space')
            if 'creator' in list_display: list_display.remove('creator')
        if 'status' in list_display:
            list_display = [f if f != 'status' else 'status_label' for f in list_display]
        return list_display

    def get_list_filter(self, request):
        list_filter = list(super().get_list_filter(request))
        if not request.user.is_superuser:
            if 'space' in list_filter: list_filter.remove('space')
            if 'creator' in list_filter: list_filter.remove('creator')
        return list_filter

    access_rules = {}
    change_form_template = 'django_admin_workflow/change_form.html'

    def message_user(self, request, message, level=messages.INFO, extra_tags="", fail_silently=False):
        if self._invalid_save_flag: return
        return super().message_user(request, message, level, extra_tags, fail_silently)

    def save_related(self, request, form, formsets, change):
        if self._invalid_save_flag: return
        super().save_related(request, form, formsets, change)

    def log_change(self, request, obj, message):
        if self._invalid_save_flag: return
        return super().log_change(request, obj, message)

    def response_change(self, request, obj):
        return super().response_change(request, obj)

    def render_change_form(self, request, context, add=False, change=False, form_url="", obj=None):
        status = 'DRAFT' if add else obj.status
        self._add_action_buttons(request, status, context)
        return super().render_change_form(request, context, add, change, form_url, obj)

    def save_model(self, request, obj, form, change):
        if not change:
            if not request.user.is_superuser:
                obj.creator = request.user
            obj.space = Space.objects.get_for_user(obj.creator)
        prev_status = obj.status
        self._invalid_save_flag = False
        status_change, had_access = self._change_state(request, obj)
        if had_access:
            if not status_change or obj.on_before_change_status(prev_status=prev_status):
                super().save_model(request, obj, form, change)
                obj.on_after_change_status(prev_status=prev_status)
        else:
            self.message_user(request, _("Something went wrong, action was not successful :-(. Please reload page ..." ),
                              level=messages.ERROR)
            self._invalid_save_flag = True

    def get_fields(self, request, obj=None):
        fields = self._get_fields_common('fields',
                                       request, obj) or super().get_fields(request, obj)
        if not request.user.is_superuser:
            if 'status' in fields: fields.remove('status')
            if 'space' in fields: fields.remove('space')
        return fields

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            rules = self._get_access_rules(request)
            if rules:
                # filter on status rules
                qs = qs.filter(status__in=rules)
                if 'filter' in rules:
                    # extra filter
                    lambfunc = rules['filter']
                    space = Space.objects.get_for_user(request.user)
                    return lambfunc(qs, space, request.user)
        return qs

    def has_user_access(self, request, rules, status):
        """
        check status with user rights
        """
        return rules and status in rules and 'actions' in rules[status]

    def _get_fields_common(self, access_type, request, obj=None):
        """
        get fields RO or RW depending on rules

        :param access_type: "fields" | "readonly_fields"
        :param request:
        :param obj: obj or None if creation
        :return: list fields or None if no rules or superuser
        """
        if not request.user.is_superuser:
            rules = self._get_access_rules(request)
            # creation
            if obj == None:
                if 'creation' in rules:
                    rules = rules['creation']
                    if rules and access_type in rules:
                        return rules[access_type]
            # modif
            else:
                if obj.status in rules:
                    if access_type in rules[obj.status]:
                        return rules[obj.status][access_type]
        return None

    def _get_access_rules(self, req):
        """
        get acces rules for user role. cache managed

        :param req: request
        :return: access_rules_client[rolegroup] or None
        """
        if req.session.session_key not in _rules_session:
            groups = req.user.groups.filter(name__in=self.access_rules.keys())
            if groups.count() == 0:
                _rules_session[req.session.session_key] = None
            else:
                _rules_session[req.session.session_key] = self.access_rules[groups[0].name]
        return _rules_session[req.session.session_key]

    def _change_state(self, request, obj):
        """
        TODO ajout logentry
        """
        status_change, had_access = False, request.user.is_superuser
        rules = self._get_access_rules(request)
        if self.has_user_access(request, rules, obj.status):
            had_access =True
            actions = rules[obj.status]['actions']
            for action in actions:
                if len(action) < 3: continue
                cmd = "_%s" % action[0]
                if cmd in request.POST:
                    if request.POST[cmd] == action[1] and obj.status != action[2]:
                        status_change = True
                        obj.status = action[2]
                        msg = _("Status has changed to %s")
                        self.message_user(request, msg % obj.status_label(),
                                          level=messages.INFO, extra_tags='extra_tags')
                        break
        return status_change, had_access

    def _add_action_buttons(self, request, status, context):
        """
        TODO
        """
        rules = self._get_access_rules(request)
        if self.has_user_access(request, rules, status):
            # TODO: do better
            data = [self._get_data_action(t) for t in rules[status]['actions'] ]
            context['workflow_actions'] = data

    def _get_data_action(self, action):
        slug, name, *x = action
        if slug == 'save':
            return {'slug':slug, 'label':name, 'style':''}
        role = RolePermission.objects.get(slug=slug)
        return {'slug':slug, 'label':role.verbose_name,
                'style':format_html('style="background:%s"' % role.bgcolor)}

# cache
_rules_session = {}


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ('color_display', 'slug',)

@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ('color_display', 'slug', 'ctype', 'groups')

