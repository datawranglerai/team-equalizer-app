# Generated by Django 2.2 on 2019-05-12 14:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0007_auto_20190428_1540'),
    ]

    operations = [
        migrations.RenameField(
            model_name='votes',
            old_name='skill_a',
            new_name='attack',
        ),
        migrations.RenameField(
            model_name='votes',
            old_name='skill_b',
            new_name='defense',
        ),
        migrations.RenameField(
            model_name='votes',
            old_name='skill_c',
            new_name='mobility',
        ),
        migrations.RenameField(
            model_name='votes',
            old_name='skill_d',
            new_name='possession',
        ),
        migrations.RenameField(
            model_name='votes',
            old_name='skill_e',
            new_name='stamina',
        ),
    ]
