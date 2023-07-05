from account.models import Profile

from django.contrib.auth.models import User, Group
from django.test import TestCase


class TestApp(TestCase):
    def test_app_on_start_create_create_default_groups(self):
        everyone = Group.objects.get(name='Everyone')
        admins = Group.objects.get(name='Admins')

        self.assertEquals(everyone.name, 'Everyone')
        self.assertEquals(admins.name, 'Admins')

    def test_anonymous_user_is_in_everyone_group(self):
        anonymous_user = User.objects.get(username='AnonymousUser')

        self.assertTrue(anonymous_user.groups.filter(name='Everyone').exists())

    def test_profile_is_creating_with_user(self):
        profile_count = Profile.objects.count()

        User.objects.create(username='Tester')

        profile_count_after_creation = Profile.objects.count()

        self.assertTrue(profile_count_after_creation - 1 == profile_count)