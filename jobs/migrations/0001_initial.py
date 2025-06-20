# Generated by Django 5.1.3 on 2025-04-29 11:24

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ApplyJobs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('custom_qns', models.JSONField(blank=True, null=True)),
                ('status', models.CharField(choices=[('applied', 'applied'), ('reviewing', 'reviewing'), ('interview_scheduled', 'interview_scheduled'), ('undecided', 'undecided'), ('shortlisted', 'shortlisted'), ('rejected', 'rejected')], default='applied', max_length=50)),
                ('viewed', models.BooleanField(default=False)),
                ('invited', models.BooleanField(default=False)),
                ('created_on', models.DateTimeField(auto_now=True)),
                ('resume_downloaded', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='JobPosts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=250)),
                ('description', models.TextField(default='')),
                ('city', models.CharField(default='', max_length=250)),
                ('country', models.CharField(max_length=250)),
                ('location_type', models.JSONField(blank=True, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('pin_code', models.CharField(blank=True, max_length=6, null=True)),
                ('state', models.CharField(blank=True, max_length=100, null=True)),
                ('type', models.JSONField(blank=True, null=True)),
                ('schedule', models.JSONField(blank=True, null=True)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('vacancy', models.IntegerField(default=0)),
                ('timeline', models.CharField(blank=True, max_length=200, null=True)),
                ('salary_min', models.IntegerField(blank=True, null=True)),
                ('salary_max', models.IntegerField(blank=True, null=True)),
                ('industry', models.CharField(blank=True, max_length=250, null=True)),
                ('salary_period', models.CharField(default='per year', max_length=50)),
                ('benefits', models.JSONField(blank=True, null=True)),
                ('supplimental_pay', models.JSONField(blank=True, null=True)),
                ('application_updations_email', models.JSONField(blank=True, null=True)),
                ('resume_required', models.BooleanField(default=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('skills', models.JSONField(blank=True, null=True)),
                ('interview_rounds', models.JSONField(blank=True, null=True)),
                ('professional_exp_year', models.IntegerField(blank=True, default=0, null=True)),
                ('professional_exp_month', models.IntegerField(blank=True, default=0, null=True)),
                ('total_experience', models.FloatField(blank=True, default=0.0, null=True)),
                ('education', models.CharField(blank=True, max_length=50, null=True)),
                ('custom_qns', models.JSONField(blank=True, null=True)),
                ('languages', models.JSONField(blank=True, null=True)),
                ('work_location', models.JSONField(blank=True, null=True)),
                ('relocate', models.BooleanField(default=False)),
                ('date_availablity', models.BooleanField(default=True)),
                ('gender', models.CharField(blank=True, choices=[('male', 'male'), ('female', 'female')], max_length=50, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('active', 'active'), ('closed', 'closed'), ('paused', 'paused')], default='active', max_length=50)),
                ('active', models.BooleanField(default=True)),
                ('views', models.IntegerField(default=0)),
                ('verified', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='SaveJobs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
