# Generated by Django 4.2.4 on 2023-09-27 00:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog_app', '0016_subscriber_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='post',
            name='categories',
            field=models.ManyToManyField(related_name='posts', to='blog_app.category'),
        ),
    ]