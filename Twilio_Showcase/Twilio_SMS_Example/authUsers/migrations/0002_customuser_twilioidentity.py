# Generated by Django 2.2.5 on 2019-09-11 23:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authUsers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='twilioIdentity',
            field=models.IntegerField(default=0),
        ),
    ]
