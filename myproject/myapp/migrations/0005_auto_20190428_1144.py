# Generated by Django 2.2 on 2019-04-28 11:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_auto_20190428_0948'),
    ]

    operations = [
        migrations.AlterField(
            model_name='votes',
            name='player',
            field=models.CharField(max_length=200),
        ),
    ]