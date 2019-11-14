# Generated by Django 2.2.6 on 2019-11-14 20:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0011_profile_grades'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='activities',
            field=models.ManyToManyField(help_text='Select at least one activity that you practice and for which you are searching for partners.', to='activities.Activity', verbose_name='activities'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='grades',
            field=models.ManyToManyField(blank=True, help_text='Select your comfortable grade for each of the activities you have chosen.', to='activities.Grade', verbose_name='grades'),
        ),
    ]
