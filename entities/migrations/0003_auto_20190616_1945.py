# Generated by Django 2.2.2 on 2019-06-16 19:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entities', '0002_auto_20190615_0753'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='UserDocuments',
            new_name='UserDocument',
        ),
    ]
