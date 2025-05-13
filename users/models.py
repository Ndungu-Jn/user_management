from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, EmailValidator

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    phone_regex = RegexValidator(
    regex=r'^\+?1?\d{9,10}$',
    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=10, blank=True)

    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f'{self.user.username} Profile'
    
    def save(self, *args, **kwargs):
        # Clean data before saving
        if self.bio:
            self.bio = self.bio.strip()
        if self.address:
            self.address = self.address.strip()
        if self.city:
            self.city = self.city.strip()
        if self.country:
            self.country = self.country.strip()
            
        super().save(*args, **kwargs)