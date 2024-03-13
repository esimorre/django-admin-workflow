from django.contrib.contenttypes.models import ContentType
from django.core.management import BaseCommand

from django_admin_workflow.management.commands._private import get_target_ctype, list_fields_model
from django_admin_workflow.models import get_workflow_contenttypes

_template = """
[GROUP_NAME]
    # filter on space
    filter = "lambda q, user_space, user: q.filter(space=user_space)"

    # fields access on creation
    [GROUP_NAME.creation]
    fields =  [FIELDS_LIST] # ALLFIELDS
    readonly_fields = [FIELDS_LIST]

    # The 'DRAFT' status is the default for all workflow models
    [GROUP_NAME.DRAFT]
    perms = [PERMISSION_LIST]
    fields =  [FIELDS_LIST] # ALLFIELDS
    readonly_fields = [FIELDS_LIST]
    actions = [ [ACTION_CODE,    ACTION_VERBOSE],
                [ACTION_CODE2,   ACTION_VERBOSE2,   STATUS_TARGET]]

#### Add others status. This is an example for the DRAFT status
#    [clients.DRAFT]
#    perms = ["can_submit"]
#    fields =  ['name', 'contact', 'status']
#    readonly_fields = ['status']
#    actions = [ ["save",     "Save"],
#                ["submit",   "Submit", "submited"],
#                ["cancel",   "Cancel",   "canceled"]]

#### Add others [GROUP_NAME] sections
"""
_template_model = """
from django_admin_workflow.models import BaseStateModel
class MyWorkflowModel(BaseStateModel):
"""

class Command(BaseCommand):
    help = "Generate a .toml workflow template file on stdout"
    def create_parser(self, prog_name, subcommand, **kwargs):
        return super().create_parser(prog_name, subcommand,
            usage="%(prog)s [-m app_label.model_name] [-t] [options] [ > workflow.toml ]",
            **kwargs)

    def add_arguments(self, parser):
        parser.add_argument("-m", "--model", metavar="app_label.model", nargs=1,
                            required=False, help="workflow model (based on BaseStateModel)")
        parser.add_argument("-t", "--model-template", action='store_true',
                        required=False, help="generate a workflow model template.")


    def handle(self, model, model_template,  *args, **options):
        msg = """
# 1. Put this in a file ie. named 'workflow.toml' in your app directory
# 2. Edit this file with real values
# 3. fill the "access_rules" field of the ModelAdmin registered for the workflow model:
#      @admin.register(MyTestModel)
#      class MyTestModelAdmin(WorkflowModelAdmin):
#          access_rules = get_workflow_data(__file__, file_data="workflow.toml")
        """

        ctype, wf_ready, explicit, nb_wf = get_target_ctype(model)
        if explicit:
            app, mod = model[0].split('.')
            self.stderr.write("The workflow model is %s.%s" % ctype.natural_key(), ending='\n')
            # test if workflow model
            if not wf_ready:
                fields = list_fields_model(ctype)
                text = _template.replace("ALLFIELDS", fields)
                print(text)
                self.stderr.write("The model mentioned is not yet ready for workflow", ending='\n')
                self.stderr.write("it just have to inherit django_admin_workflow.models.BaseStateModel", ending='\n')
                return
        else:
            if nb_wf > 1:
                self.stderr.write("The -m option is required", ending='\n')
                return

        if ctype:
            fields = list_fields_model(ctype)
            text = _template.replace("ALLFIELDS", fields)
            print (text)
            self.stderr.write(fields, ending='\n')
        else:
            # no model found
            text = _template.replace("# ALLFIELDS", "")
            print (text)
            self.stderr.write("no workflow model found; the template is basic", ending='\n')
            self.stderr.write("run again after adding a model like below:", ending='\n')
            self.stderr.write(_template_model, ending='\n')
            for f in ('one_field', '...'):
                self.stderr.write("    %s =\tmodels.AnyField(...)" % f, ending='\n')




