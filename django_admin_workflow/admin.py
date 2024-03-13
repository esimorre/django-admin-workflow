from django.contrib import admin, messages
from django.contrib.admin.models import LogEntry

from .models import Space, Status, RolePermission


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
    access_rules = {}
    change_form_template = 'django_admin_workflow/change_form.html'
    def log_change(self, request, obj, message):
        return super().log_change(request, obj, message)

    def response_change(self, request, obj):
        return super().response_change(request, obj)

    def construct_change_message(self, request, form, formsets, add=False):
        return super().construct_change_message(request, form, formsets, add)

    def render_change_form(self, request, context, add=False, change=False, form_url="", obj=None):
        if change:
            self._add_action_buttons(request, obj.status, context)
        return super().render_change_form(request, context, add, change, form_url, obj)

    def save_model(self, request, obj, form, change):
        if not change:
            if not request.user.is_superuser:
                obj.creator = request.user
            obj.space = Space.objects.get_for_user(obj.creator)
        self._change_state(request, obj)
        super().save_model(request, obj, form, change)

    def get_fields(self, request, obj=None):
        fields = self._get_fields_common('fields',
                                       request, obj) or super().get_fields(request, obj)
        if not request.user.is_superuser:
            if 'status' in fields: fields.remove('status')
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
        rules = self._get_access_rules(request)
        if rules and obj.status in rules and 'actions' in rules[obj.status]:
            actions = rules[obj.status]['actions']
            for action in actions:
                if len(action) < 3: continue
                cmd = "_%s" % action[0]
                if cmd in request.POST:
                    if request.POST[cmd] == action[1]:
                        obj.status = action[2]
                        self.message_user(request, "change status TODO",
                                          level=messages.WARNING, extra_tags='extra_tags')
                        return

    def _add_action_buttons(self, request, status, context):
        """
        TODO
        """
        rules = self._get_access_rules(request)
        if rules and status in rules and 'actions' in rules[status]:
            data = [(t[0], t[1]) for t in rules[status]['actions'] ]
            context['workflow_actions'] = data



# cache
_rules_session = {}


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ('color_display', 'slug',)

@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ('color_display', 'slug', 'ctype', 'groups')

