# Generated by Django 2.1.7 on 2019-07-09 07:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rbac', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='permission',
            name='url',
            field=models.CharField(max_length=64, verbose_name='权限'),
        ),
    ]