# Generated by Django 3.0.4 on 2020-03-15 16:52

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='employee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('emplyee_name', models.CharField(max_length=300)),
                ('employee_ID', models.IntegerField(default=999999)),
                ('activity_text', models.TextField(default='000', max_length=300)),
                ('quarantined', models.BooleanField(blank=True, default=False)),
                ('infected', models.BooleanField(blank=True, default=False)),
            ],
        ),
        migrations.CreateModel(
            name='question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_text', models.CharField(blank=True, max_length=200)),
                ('answer_1', models.CharField(blank=True, max_length=200)),
                ('answer_2', models.CharField(blank=True, max_length=200)),
                ('answer_3', models.CharField(blank=True, max_length=200)),
                ('correct_answer', models.CharField(blank=True, max_length=200)),
            ],
        ),
    ]
