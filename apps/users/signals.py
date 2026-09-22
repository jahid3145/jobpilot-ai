from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CandidateProfile


@receiver(post_save, sender=get_user_model())
def create_candidate_profile(sender, instance, created, **kwargs):
    if created:
        CandidateProfile.objects.create(user=instance, full_name=instance.get_full_name())

