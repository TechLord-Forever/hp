# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-03 09:05
from __future__ import unicode_literals

import account.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import jsonfield.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(max_length=255, unique=True, verbose_name='Username')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='Email')),
                ('gpg_fingerprint', models.CharField(blank=True, max_length=40, null=True)),
                ('registered', models.DateTimeField(auto_now_add=True)),
                ('registration_method', models.SmallIntegerField(choices=[(0, 'Via Website'), (1, 'In-Band Registration'), (2, 'Manually'), (9, 'Unknown')], default=0)),
                ('confirmed', models.DateTimeField(blank=True, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name_plural': 'users',
                'verbose_name': 'user',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Confirmation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('to', models.EmailField(blank=True, max_length=254, null=True, verbose_name='Recipient')),
                ('key', models.CharField(default=account.models.default_key, max_length=40)),
                ('expires', models.DateTimeField(default=account.models.default_expires)),
                ('purpose', models.CharField(blank=True, max_length=16, null=True)),
                ('payload', jsonfield.fields.JSONField(default=account.models.default_payload)),
                ('language', models.CharField(max_length=2)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='confirmations', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GpgKey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('fingerprint', models.CharField(max_length=40)),
                ('key', models.TextField()),
                ('expires', models.DateTimeField(blank=True, null=True)),
                ('revoked', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gpg_keys', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'GPG keys',
                'verbose_name': 'GPG key',
            },
        ),
        migrations.CreateModel(
            name='UserLogEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('address', models.GenericIPAddressField(null=True)),
                ('message', models.TextField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='log_entries', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'User activity logs',
                'verbose_name': 'User activity log',
            },
        ),
        migrations.AlterUniqueTogether(
            name='gpgkey',
            unique_together=set([('user', 'fingerprint')]),
        ),
    ]
