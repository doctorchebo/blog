# Generated by Django 4.2.6 on 2024-04-09 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0003_alter_pagevisit_visit_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='pagevisit',
            name='ip_address',
            field=models.GenericIPAddressField(blank=True, null=True),
        ),
    ]
