from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
    GENDER_CHOICES = {
        "F": "Female",
        "M": "Man",
        "O": "Other",
    }
    profile_user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(blank=True, null=True)
    date_of_joined = models.DateTimeField(auto_now_add=True)
    date_of_edited = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.profile_user.username
    
@receiver(post_save, sender=User)
def auto_create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(profile_user=instance)