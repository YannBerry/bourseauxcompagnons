# Generated by Django 2.1.3 on 2018-12-16 22:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('outings', '0005_auto_20181214_2249'),
    ]

    operations = [
        migrations.AlterField(
            model_name='outing',
            name='c2c_link',
            field=models.URLField(blank=True, help_text='Ce champ est facultatif mais important car il améliore la lecture de votre sortie par les internautes. Camptocamp est une très bonne source de topos.', verbose_name='lien URL vers un topo de la sortie'),
        ),
    ]
