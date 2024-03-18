# Generated by Django 5.0.3 on 2024-03-18 13:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_admin_workflow', '0006_rename_active_usersetting_email_active_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usersetting',
            name='email_active',
            field=models.BooleanField(default=True, verbose_name='email notification active'),
        ),
        migrations.AlterField(
            model_name='usersetting',
            name='reactive_date',
            field=models.DateField(blank=True, null=True, verbose_name='reactivation date'),
        ),
    ]
