# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-06-01 12:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('offer', '0006_auto_20170504_0616'),
        ('voucher', '0002_auto_20170418_2132'),
    ]

    operations = [
        migrations.CreateModel(
            name='VoucherSet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('count', models.IntegerField(verbose_name='Amount')),
                ('code_length', models.IntegerField(default=12, verbose_name='Length of Code')),
                ('description', models.TextField(verbose_name='Description')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('start_datetime', models.DateTimeField(verbose_name='Start datetime')),
                ('end_datetime', models.DateTimeField(verbose_name='End datetime')),
                ('offer', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='voucher_set', to='offer.ConditionalOffer', verbose_name='Offer')),
            ],
            options={
                'verbose_name': 'VoucherSet',
                'verbose_name_plural': 'VoucherSets',
                'get_latest_by': 'date_created',
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='voucher',
            name='voucher_set',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='vouchers', to='voucher.VoucherSet'),
        ),
    ]
