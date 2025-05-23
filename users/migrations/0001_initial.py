# Generated by Django 5.2 on 2025-04-21 04:43

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RenterProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(blank=True, max_length=100)),
                ('last_name', models.CharField(blank=True, max_length=100)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('phone_number', models.CharField(blank=True, max_length=20)),
                ('current_address', models.CharField(blank=True, max_length=255)),
                ('current_city', models.CharField(blank=True, max_length=100)),
                ('current_state', models.CharField(blank=True, max_length=100)),
                ('current_zip_code', models.CharField(blank=True, max_length=20)),
                ('employer_name', models.CharField(blank=True, max_length=255)),
                ('job_title', models.CharField(blank=True, max_length=100)),
                ('monthly_income', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('employment_start_date', models.DateField(blank=True, null=True)),
                ('ssn_last_four', models.CharField(blank=True, help_text='Last 4 digits of SSN', max_length=4)),
                ('emergency_contact_name', models.CharField(blank=True, max_length=100)),
                ('emergency_contact_phone', models.CharField(blank=True, max_length=20)),
                ('lease_term_preference', models.CharField(blank=True, help_text='e.g., 6 months, 12 months', max_length=50)),
                ('move_in_date', models.DateField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='renter_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
