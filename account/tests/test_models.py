from django.contrib.auth.models import User
from django.test import TestCase


class TestUserModel(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='pat')

    def test_get_absolute_url(self):
        self.assertEquals(self.user.get_absolute_url(), '/account/profile/pat/')