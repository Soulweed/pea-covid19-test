# Generated by Django 3.0.4 on 2020-03-23 06:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myworkplace', '0009_auto_20200320_1654'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='LEAVE_end_date',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='employee',
            name='LEAVE_start_date',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='employee',
            name='WFH_end_date',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='employee',
            name='WFH_start_date',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='employee',
            name='active_status',
            field=models.CharField(blank=True, choices=[('PEA', 'PEA'), ('WFH', 'WFH'), ('LEAVE', 'Leave'), ('COVID', 'COVID')], max_length=6),
        ),
        migrations.AddField(
            model_name='employee',
            name='approved_status',
            field=models.CharField(blank=True, choices=[('Idle', 'Idle'), ('WFH', 'WFH'), ('LEAVE', 'Leave'), ('COVID', 'COVID')], max_length=6),
        ),
        migrations.AddField(
            model_name='employee',
            name='challenge',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='employee',
            name='daily_update',
            field=models.BooleanField(default=False),
        ),
    ]
