# Generated by Django 2.2.4 on 2019-09-26 21:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authUsers', '0004_auto_20190923_1544'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='AuthyIdentity',
        ),
    ]
