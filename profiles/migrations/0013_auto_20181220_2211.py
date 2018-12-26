# Generated by Django 2.1.3 on 2018-12-20 22:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0012_auto_20181217_2334'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='birthdate',
            field=models.DateField(blank=True, help_text='Utilisée pour indiquer votre âge sur votre profil publique. Exemple : 25/05/2000', null=True, verbose_name='date de naissance'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='public_profile',
            field=models.BooleanField(default=True, help_text='Si votre profil est public alors il apparait dans la liste des profils.', verbose_name='profil public'),
        ),
    ]
