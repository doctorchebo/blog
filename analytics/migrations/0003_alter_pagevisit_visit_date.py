# Generated by Django 4.2.6 on 2023-10-27 01:12

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0002_pagevisit_end_date_alter_pagevisit_duration_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pagevisit',
            name='visit_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
