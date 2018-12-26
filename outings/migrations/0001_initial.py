# Generated by Django 2.1.3 on 2018-12-01 14:30

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('activities', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Outing',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('slug', models.SlugField(max_length=60, unique=True)),
                ('description', models.TextField()),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('c2c_link', models.URLField(blank=True)),
                ('activities', models.ManyToManyField(to='activities.Activity')),
            ],
            options={
                'verbose_name': 'sortie',
            },
        ),
    ]
