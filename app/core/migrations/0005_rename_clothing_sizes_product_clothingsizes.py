# Generated by Django 3.2.25 on 2025-01-04 02:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20250104_0223'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='clothing_sizes',
            new_name='clothingSizes',
        ),
    ]
