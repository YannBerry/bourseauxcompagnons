# Generated by Django 2.2.4 on 2019-08-22 15:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('outings', '0002_outing_author'),
    ]

    operations = [
        migrations.AlterField(
            model_name='outing',
            name='start_date',
            field=models.DateField(verbose_name='start'),
        ),
    ]
