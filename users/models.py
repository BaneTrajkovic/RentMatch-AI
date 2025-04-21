from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class RenterProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='renter_profile')
    
    # Personal Information
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    
    # Current Address
    current_address = models.CharField(max_length=255, blank=True)
    current_city = models.CharField(max_length=100, blank=True)
    current_state = models.CharField(max_length=100, blank=True)
    current_zip_code = models.CharField(max_length=20, blank=True)
    
    # Employment Information
    employer_name = models.CharField(max_length=255, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    monthly_income = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    employment_start_date = models.DateField(null=True, blank=True)
    
    # Additional Information
    ssn_last_four = models.CharField(max_length=4, blank=True, help_text="Last 4 digits of SSN")
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    
    # Preferences
    lease_term_preference = models.CharField(max_length=50, blank=True, help_text="e.g., 6 months, 12 months")
    move_in_date = models.DateField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Renter Profile"

    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.user.username

# Signal to create RenterProfile when User is created
@receiver(post_save, sender=User)
def create_renter_profile(sender, instance, created, **kwargs):
    if created:
        RenterProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_renter_profile(sender, instance, **kwargs):
    # This handler should only run if the profile exists
    if hasattr(instance, '_renter_profile_cache'):
        instance.renter_profile.save()
    else:
        try:
            # Get the profile if it exists
            profile = RenterProfile.objects.get(user=instance)
            profile.save()
        except RenterProfile.DoesNotExist:
            # Create if it doesn't exist
            RenterProfile.objects.create(user=instance)
