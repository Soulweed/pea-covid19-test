# Generated by Django 3.0.4 on 2020-03-28 12:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myworkplace', '0021_director_ga_emails'),
    ]

    operations = [
        migrations.CreateModel(
            name='Director_Area_Emails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('employee_id', models.CharField(max_length=255)),
                ('ref2', models.CharField(max_length=255)),
                ('ref1', models.CharField(max_length=255)),
                ('lastref', models.CharField(max_length=255)),
                ('email', models.CharField(max_length=255)),
            ],
        ),
    ]
