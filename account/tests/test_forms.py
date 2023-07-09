from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from account.forms import UserRegisterForm


class TestUserRegisterForm(TestCase):
    def test_form_create_user_if_data_is_correct(self):
        users_count_before_post = User.objects.count()
        form = UserRegisterForm(data={'username': 'Pat',
                                      'email': 'patmat@localhost.com',
                                      'password': '123',
                                      'confirm_password': '123'})

        self.assertTrue(form.is_valid())

        form.save()
        users_count_after_form_save = User.objects.count()
        self.assertTrue(users_count_before_post + 1 == users_count_after_form_save)

    def test_form_validation_false_if_passwords_not_same(self):
        form = UserRegisterForm(data={'username': 'Pat',
                                      'email': 'patmat@localhost.com',
                                      'password': '123',
                                      'confirm_password': '321'})

        self.assertFalse(form.is_valid())

    def test_form_validation_false_if_email_is_used(self):
        User.objects.create(username='Test', email='patmat@localhost.com')

        form = UserRegisterForm(data={'username': 'Pat',
                                      'email': 'patmat@localhost.com',
                                      'password': '123',
                                      'confirm_password': '123'})

        self.assertFalse(form.is_valid())

