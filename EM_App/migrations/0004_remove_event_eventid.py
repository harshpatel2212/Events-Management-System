# Generated by Django 4.0.1 on 2022-01-27 11:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('EM_App', '0003_rename_eventid_event_eventid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='eventID',
        ),
    ]