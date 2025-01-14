from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=255, blank=True)
    points = models.PositiveIntegerField(default = 1000)
    validity = models.FloatField(default = 100) # Validity of the user's account
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):
    profile, created = Profile.objects.get_or_create(user=instance)
    # Only update the address if it is empty
    if not profile.address:
        profile.address = instance.profile.address if hasattr(instance, 'profile') else ''
    profile.save()