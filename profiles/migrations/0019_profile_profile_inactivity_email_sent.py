# Generated by Django 4.0.3 on 2022-04-22 12:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0018_alter_customuser_language'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='profile_inactivity_email_sent',
            field=models.JSONField(default=list),
        ),
    ]
