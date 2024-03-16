# django-admin-workflow


An application for django that allows you to focus on data modeling,
data process and functionality without investing in the user interface
by taking advantage of the capabilities of the django admin application.

Functionality first, cosmetics and pretty panels can wait.

This application was designed to stay as close as possible to the spirit of contrib admin.

The goal is to add data security to CRUD through workflow: partitioning and management by roles

Detailed documentation is in the "docs" directory (soon).

## Quick start
(First, it is advisable to follow the following in "dry run" mode by examining the apptest application).

1. Add "django_admin_workflow" to your INSTALLED_APPS setting like this::
```python
    INSTALLED_APPS = [
        "django_admin_workflow",
        ...,
    ]
```

2. Edit your project urls.py like this
```python
# admin.sites.site.index_title = "Welcome"
# admin.sites.site.site_title = "Django workflow"
# admin.sites.site.site_header = "Workflow pour Django"

urlpatterns = [
    path('', admin.site.urls),
]
```

3. Use BaseStateModel instead of models.ModelAdmin on the object to process
```python
from django_admin_workflow.models import BaseStateModel

class MyTestModel(BaseStateModel):
    a_field = models.XXXFields(...)
    ...
```

3. Similarly, use WorkflowModelAdmin instead of models.ModelAdmin

4. Run ``python manage.py migrate`` to create the models.

5. Run the gen_workflow_template command to help define the workflow
```bash
python manage.py gen_workflow_template -h
usage: manage.py gen_workflow_template [-m app_label.model_name] [options] [ > workflow.toml ]
Generate a .toml workflow template file on stdout
```

6. Edit the .toml file to define the workflow groups and roles, as in this example
```toml
# Groupe clients
[clients]
    filter = "lambda q, user_space, user: q.filter(space=user_space)"

    # création d'un objet dans le workflow
    [clients.creation]
    fields =  ['name', 'contact', 'status']
    readonly_fields = ['contact', 'status']

    # Etat DRAFT
    [clients.DRAFT]
    fields =  ['name', 'contact', 'status']
    readonly_fields = ['contact', 'status']
    actions = [ ["save",     "Enregistrer"],
                ["can_submit",   "Soumettre", "submited"],
                ["can_cancel",   "Annuler",   "canceled"]]

```

7. Use the import_workflow command to create the groups, permissions, status, roles
in the database from the workflow file (test it before with the --dry-run option)
```
python manage.py import_workflow -h 
usage: manage.py import_workflow workflow_file [-m app_label.model_name] [-d] [--dry-run] [options]
import a workflow definition file (see gen_workflow_template) to generate objects in db. This command generates groups and permissions.
```

8. Use the add_sample command to populate the database with pre-configured users
```
python manage.py add_sample -h
usage: manage.py add_sample [-a [username=admin [passwd=username]]]  [options]
Populate database with some sample data
```

9. Enter the workflow file on the model's admin class
```python
@admin.register(MyTestModel)
class MyTestModelAdmin(WorkflowModelAdmin):
    access_rules = get_workflow_data(__file__, file_data="workflow.toml")
    list_display = ...
```

10. Start the development server and visit the admin as super-user, browse the panel,
you will be able to configure the spaces (partitioning), statuses and roles.

11. log in as a regular user...and do your job :)