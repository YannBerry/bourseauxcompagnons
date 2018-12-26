# Generated by Django 2.1.3 on 2018-12-17 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('outings', '0016_auto_20181216_2308'),
    ]

    operations = [
        migrations.AlterField(
            model_name='outing',
            name='start_date',
            field=models.DateField(help_text='Exemple français : 25/05/2020', verbose_name='début'),
        ),
        migrations.AlterField(
            model_name='outing',
            name='title',
            field=models.CharField(help_text="70 caractères max.<br>Exemple : 'Traversée de la Meije - Voie normale - Bivouac Grand Pic'.", max_length=70, verbose_name='titre'),
        ),
    ]
