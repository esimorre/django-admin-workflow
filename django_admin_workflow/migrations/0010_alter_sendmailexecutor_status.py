# Generated by Django 5.0.3 on 2024-04-08 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_admin_workflow', '0009_sendmailexecutor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sendmailexecutor',
            name='status',
            field=models.SlugField(blank=True, help_text='status of objects to be processed', max_length=20, null=True),
        ),
    ]
