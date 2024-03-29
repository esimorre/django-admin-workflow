# Generated by Django 5.0.3 on 2024-03-13 14:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_admin_workflow', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='configrolestatus',
            name='config_role',
        ),
        migrations.RemoveField(
            model_name='configroleadd',
            name='config_role',
        ),
        migrations.RemoveField(
            model_name='configrolestatus',
            name='permission',
        ),
        migrations.RemoveField(
            model_name='configrolestatus',
            name='status',
        ),
        migrations.RemoveField(
            model_name='rolestatusaction',
            name='config_role',
        ),
        migrations.RemoveField(
            model_name='configworkflow',
            name='ctype',
        ),
        migrations.RemoveField(
            model_name='rolestatusaction',
            name='status_change',
        ),
        migrations.DeleteModel(
            name='ConfigRole',
        ),
        migrations.DeleteModel(
            name='ConfigRoleAdd',
        ),
        migrations.DeleteModel(
            name='ConfigRoleStatus',
        ),
        migrations.DeleteModel(
            name='ConfigWorkflow',
        ),
        migrations.DeleteModel(
            name='RoleStatusAction',
        ),
    ]
