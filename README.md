# django-admin-workflow
*Like a state-machine (Get on up !)*

An application for django that allows you to focus on data modeling,
data process and functionality without investing in the user interface
by taking advantage of the capabilities of the django admin application.

Functionality first, cosmetics and pretty panels can wait.

This application was designed to stay as close as possible to the spirit of contrib admin.

The goal is to add data security to CRUD through workflow: partitioning and management by roles

## Basic principles
Let's illustrate them by example
 * given
   * user1 belongs to the "Dept1" and "customers" groups
   * user2 belongs to the "Dept2" and "customers" groups
 * user2 sees nothing of the data created by user1
 * user1 can only do what the "customers" group allows
 * "Dept1" is a partition group (space)
 * "customers" is a role group.
 * these below no longer have a global scope (except for the superuser):
   * the "fields" and "read_onlyfields" attributes of model admin
   * the permissions on the model
   * it depend on the user role and status of the model instance.
 * the admin interface is no longer reserved for backend use, but also for
the end user interface
 
## Quick start
(First, it is advisable to follow the following in "dry run" mode by browsing the vacation application).

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
# Group employees
[employees]
    filter = "lambda q, user_space, user: q.filter(space=user_space)"

    # création d'un objet dans le workflow
    [employees.creation]
        fields =  ['begin', 'end', 'comment']

    # Etat DRAFT
    [employees.DRAFT]
        fields =  ['begin', 'end', 'comment']
        actions = [ ["save",     "Save"],
                    ["submit",   "Submit", "check"],
                    ["cancel",   "Cancel",   "canceled"]]
# Group managers
[managers]
    filter = "lambda q, user_space, user: q.filter(space=user_space)"

    [managers.submited]
        fields =  ['begin', 'end', 'comment', 'status']
        readonly_fields = ['status']
        actions = [ ["approve",   "Approve", "approved"],
                    ["reject",   "Reject",   "rejected"]]

# autorun
[auto]
    [auto.check]
        actions = [ ['', 'insufficient balance', 'DRAFT'],
                    ['', '', 'submited']]

    [auto.approved]
        actions = [ ['', '', 'archived']]

    [auto.rejected]
    [auto.archived]
    [auto.fail_sent]
```

A view allows the graphical display of the workflow using the mermaid library:
```mermaid
---
title: Workflow
---
graph LR

    DRAFT["fa:fa-tag DRAFT<hr/>fa:fa-user-pen fa:fa-list<hr/>fa:fa-user-group employees"]

    check["fa:fa-tag check<hr/>fa:fa-gears auto"]

    canceled["fa:fa-tag canceled<hr/>fa:fa-trash-can "]

    submited["fa:fa-tag submited<hr/>fa:fa-user-pen fa:fa-list<hr/>fa:fa-user-group managers"]

    approved["fa:fa-tag approved<hr/>fa:fa-gears auto"]

    rejected["fa:fa-tag rejected<hr/>fa:fa-gears auto"]

    archived["fa:fa-tag archived<hr/>fa:fa-gears auto"]

    fail_sent["fa:fa-tag fail_sent<hr/>fa:fa-gears auto"]



    DRAFT -- Submit --> check

    DRAFT -- Cancel --> canceled

    submited -- Approve --> approved

    submited -- Reject --> rejected

    check -- insufficient balance --> DRAFT

    check --> submited

    approved --> archived
```

7. Use the import_workflow command to create the groups, permissions, status, roles
in the database from the workflow file (test it before with the --dry-run option)
```
python manage.py import_workflow -h 
usage: manage.py import_workflow workflow_file [-m app_label.model_name] [-d] [--dry-run] [options]
import a workflow definition file (see gen_workflow_template) to generate objects in db. This command generates groups and permissions.
```

8. Use the add_sample command to populate the database with pre-configured users and spaces
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

*Stay on the scene*
