# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-22 00:51
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import utils.helpers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('geo_and_languages', '0001_initial'),
        ('organizations', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Eligibility',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('eligibility_details', models.TextField(blank=True)),
                ('minimum_age', models.TextField(blank=True)),
                ('maximum_age', models.TextField(blank=True)),
                ('veteran_status', models.TextField(blank=True)),
                ('maximum_income', models.TextField(blank=True)),
                ('taxonomy_detail', models.TextField(blank=True)),
                ('area_description', models.TextField(blank=True)),
                ('required_document', models.TextField(blank=True)),
                ('area', models.ManyToManyField(blank=True, to='geo_and_languages.County')),
            ],
            bases=(models.Model, utils.helpers.CreationUpdatedInstances),
        ),
        migrations.CreateModel(
            name='EligibilityUpdate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('eligibility_details', models.TextField(blank=True)),
                ('minimum_age', models.TextField(blank=True)),
                ('maximum_age', models.TextField(blank=True)),
                ('veteran_status', models.TextField(blank=True)),
                ('maximum_income', models.TextField(blank=True)),
                ('taxonomy_detail', models.TextField(blank=True)),
                ('area_description', models.TextField(blank=True)),
                ('required_document', models.TextField(blank=True)),
                ('is_processed', models.BooleanField(default=False)),
                ('is_marked_deleted', models.BooleanField(default=False)),
                ('area', models.ManyToManyField(blank=True, to='geo_and_languages.County')),
                ('eligibility', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='services.Eligibility')),
            ],
        ),
        migrations.CreateModel(
            name='Program',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('organization', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='organizations.Organization')),
            ],
            bases=(models.Model, utils.helpers.CreationUpdatedInstances),
        ),
        migrations.CreateModel(
            name='ProgramUpdate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('is_processed', models.BooleanField(default=False)),
                ('is_marked_deleted', models.BooleanField(default=False)),
                ('created_by', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('organization', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='organizations.Organization')),
                ('program', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='services.Program')),
            ],
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('status', models.CharField(blank=True, max_length=255)),
                ('application_process', models.CharField(blank=True, max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('interpretation_services', models.ManyToManyField(blank=True, to='geo_and_languages.Language')),
                ('program', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='services.Program')),
                ('program_update', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='services.ProgramUpdate')),
            ],
            bases=(models.Model, utils.helpers.CreationUpdatedInstances),
        ),
        migrations.CreateModel(
            name='ServiceUpdate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('status', models.CharField(blank=True, max_length=255)),
                ('application_process', models.CharField(blank=True, max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('is_processed', models.BooleanField(default=False)),
                ('is_marked_deleted', models.BooleanField(default=False)),
                ('created_by', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('interpretation_services', models.ManyToManyField(blank=True, to='geo_and_languages.Language')),
                ('program', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='services.Program')),
                ('program_update', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='services.ProgramUpdate')),
                ('service', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='services.Service')),
            ],
        ),
        migrations.CreateModel(
            name='Taxonomy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.AddField(
            model_name='serviceupdate',
            name='taxonomy_ids',
            field=models.ManyToManyField(blank=True, to='services.Taxonomy'),
        ),
        migrations.AddField(
            model_name='service',
            name='taxonomy_ids',
            field=models.ManyToManyField(blank=True, to='services.Taxonomy'),
        ),
        migrations.AddField(
            model_name='programupdate',
            name='taxonomy_ids',
            field=models.ManyToManyField(blank=True, to='services.Taxonomy'),
        ),
        migrations.AddField(
            model_name='program',
            name='taxonomy_ids',
            field=models.ManyToManyField(blank=True, to='services.Taxonomy'),
        ),
        migrations.AddField(
            model_name='eligibilityupdate',
            name='service',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='services.Service'),
        ),
        migrations.AddField(
            model_name='eligibilityupdate',
            name='service_update',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='services.ServiceUpdate'),
        ),
        migrations.AddField(
            model_name='eligibilityupdate',
            name='taxonomy',
            field=models.ManyToManyField(blank=True, to='services.Taxonomy'),
        ),
        migrations.AddField(
            model_name='eligibility',
            name='service',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='services.Service'),
        ),
        migrations.AddField(
            model_name='eligibility',
            name='service_update',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='services.ServiceUpdate'),
        ),
        migrations.AddField(
            model_name='eligibility',
            name='taxonomy',
            field=models.ManyToManyField(blank=True, to='services.Taxonomy'),
        ),
    ]
