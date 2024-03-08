from django.contrib import admin
from django.contrib.admin.models import LogEntry

from .models import Space


@admin.register(Space)
class SpaceAdmin(admin.ModelAdmin):
    pass

@admin.register(LogEntry)
class LogEntry(admin.ModelAdmin):
    list_display = ('action_time', 'user', 'object_repr', 'change_message')
    date_hierarchy = 'action_time'
    list_filter = ('user',)
    search_fields = ('object_repr',)
    search_help_text = "nom d'objet"


# Gestionnaire des vues admin respectant les règles groupe/permissions/champs exposés
class WorkflowModelAdmin(admin.ModelAdmin):
    access_rules = {}
    change_form_template = 'django_admin_workflow/change_form.html'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.creator = request.user.username
            obj.space = Space.objects.user_space_groupname(request.user)
        super().save_model(request, obj, form, change)

    def get_fields(self, request, obj=None):
        return self._get_fields_common('fields',
                                       request, obj) or super().get_fields(request, obj)

    def get_readonly_fields(self, request, obj=None):
        return self._get_fields_common('readonly_fields',
                                       request, obj) or super().get_readonly_fields(request, obj)

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
                    if access_type in rules:
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


# cache
_rules_session = {}
