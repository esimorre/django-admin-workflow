# django-admin-workflow


An app for django admin that adds workflow to your objects

Detailed documentation is in the "docs" directory.

## Quick start

1. Add "django_admin_workflow" to your INSTALLED_APPS setting like this::

```
    INSTALLED_APPS = [
        "django_admin_workflow",
        ...,
    ]
```

2. Edit your project urls.py like this::

```
# admin.sites.site.index_title = "Welcome"
# admin.sites.site.site_title = "Django workflow"
# admin.sites.site.site_header = "Workflow pour Django"

urlpatterns = [
    path('', admin.site.urls),
]
```

```
from django_admin_workflow.models import BaseStateModel

class MyTestModel(BaseStateModel):
    a_field = models.XXXFields(...)
    ...
```

```
python manage.py gen_workflow_template -h
usage: manage.py gen_workflow_template [-m app_label.model_name] [options] [ > workflow.toml ]
Generate a .toml workflow template file on stdout
```

```
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

```
python manage.py import_workflow -h 
usage: manage.py import_workflow workflow_file [-m app_label.model_name] [-d] [--dry-run] [options]
import a workflow definition file (see gen_workflow_template) to generate objects in db. This command generates groups and permissions.
```

```
python manage.py add_sample -h
usage: manage.py add_sample [-a [username=admin [passwd=username]]]  [options]
Populate database with some sample data
```


3. Run ``python manage.py migrate`` to create the models.

4. Start the development server and visit the admin to create a poll.

5. Visit the ``/polls/`` URL to participate in the poll.