# Generated by Django 3.0.4 on 2020-03-28 09:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myworkplace', '0018_director_3_emails_director_4_emails'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='director_approve_email',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='director_approve_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='director_approve_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='director_approve_position',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
