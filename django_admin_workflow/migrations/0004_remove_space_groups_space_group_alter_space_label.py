# Generated by Django 5.0.3 on 2024-03-08 08:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('django_admin_workflow', '0003_space_label'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='space',
            name='groups',
        ),
        migrations.AddField(
            model_name='space',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='workspaces', to='auth.group', verbose_name='groupe associé'),
        ),
        migrations.AlterField(
            model_name='space',
            name='label',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
    ]
