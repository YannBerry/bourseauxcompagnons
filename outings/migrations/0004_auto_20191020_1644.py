# Generated by Django 2.2.4 on 2019-10-20 14:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('outings', '0003_auto_20190822_1745'),
    ]

    operations = [
        migrations.AlterField(
            model_name='outing',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='author'),
        ),
    ]
