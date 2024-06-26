# Generated by Django 5.0.3 on 2024-04-12 12:38

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('django_admin_workflow', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
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
        migrations.CreateModel(
            name='UserAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('provision', models.PositiveIntegerField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vacations', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Vacation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.SlugField(default='DRAFT', max_length=20)),
                ('begin', models.DateField(verbose_name='start')),
                ('end', models.DateField()),
                ('comment', models.TextField(max_length=100)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='creator')),
                ('space', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='django_admin_workflow.space', verbose_name='space')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='VacationExecutor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.SlugField(blank=True, help_text='status of objects to be processed', max_length=20, null=True)),
                ('last_run_datetime', models.DateTimeField(blank=True, null=True)),
                ('last_OK', models.BooleanField(default=False)),
                ('running', models.BooleanField(default=False)),
                ('space', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='django_admin_workflow.space', verbose_name='space')),
            ],
            options={
                'verbose_name': 'Executor',
                'abstract': False,
            },
        ),
    ]
