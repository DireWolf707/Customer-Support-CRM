# Generated by Django 4.0 on 2021-12-11 11:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0005_ticket_by_call'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='call_sid',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
