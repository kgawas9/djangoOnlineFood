# Generated by Django 4.1.1 on 2023-02-26 08:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='Payment',
            new_name='payment',
        ),
    ]
