# Generated by Django 2.2.4 on 2019-10-23 12:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('availabilities', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='availability',
            name='description',
            field=models.TextField(blank=True, verbose_name='description'),
        ),
    ]
