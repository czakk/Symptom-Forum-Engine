from account.models import Profile

from django.db.models.signals import post_migrate, post_save
from django.contrib.auth.models import Group, User
from django.dispatch import receiver

@receiver(post_migrate)
def create_default_groups(sender, **kwargs):
    Group.objects.get_or_create(name='Everyone')
    Group.objects.get_or_create(name='Admins')

@receiver(post_save, sender=User)
def user_to_everyone_group(sender, instance, created, **kwargs):
    if created:
        everyone_group = Group.objects.get(name='Everyone')
        instance.groups.add(everyone_group)

        Profile.objects.create(user=instance)