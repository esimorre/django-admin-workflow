# Generated by Django 5.0.3 on 2024-04-08 18:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_admin_workflow', '0010_alter_sendmailexecutor_status'),
        ('vacation', '0003_alter_vacationexecutor_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='MailExecutor',
            fields=[
                ('sendmailexecutor_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='django_admin_workflow.sendmailexecutor')),
            ],
            options={
                'verbose_name': 'Executor',
                'abstract': False,
            },
            bases=('django_admin_workflow.sendmailexecutor',),
        ),
    ]