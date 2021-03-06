# Generated by Django 2.2.4 on 2019-08-22 15:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0006_auto_20190819_1422'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='availability_area',
            field=models.CharField(help_text="Examples: 'Rhône-Alpes' or 'Around Grenoble, Chambéry, Lyon' or 'All the french Alpes'.", max_length=250, verbose_name='availability area (further details)'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='birthdate',
            field=models.DateField(blank=True, help_text='Used to display your age on your public profile.', null=True, verbose_name='birthdate'),
        ),
    ]
