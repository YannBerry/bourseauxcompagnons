# Generated by Django 2.1.3 on 2018-12-17 23:34

from django.db import migrations, models
import profiles.models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0011_auto_20181217_2327'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='profile',
            options={'ordering': ['-last_update'], 'verbose_name': 'profil', 'verbose_name_plural': 'profils'},
        ),
        migrations.AlterField(
            model_name='profile',
            name='activities',
            field=models.ManyToManyField(to='activities.Activity', verbose_name='activités'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='age',
            field=models.IntegerField(blank=True, null=True, verbose_name='âge'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='birthdate',
            field=models.DateField(blank=True, help_text='Utilisée pour indiquer votre âge sur votre profil publique.', null=True, verbose_name='date de naissance'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='last_update',
            field=models.DateTimeField(auto_now=True, verbose_name='dernière mise à jour'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to=profiles.models.user_directory_path_pict, verbose_name='photo de profil'),
        ),
    ]
