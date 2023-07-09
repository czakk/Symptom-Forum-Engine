from django.conf import settings
from django.contrib.auth import get_user
from django.contrib.auth.models import User, Group
from django.test import TestCase, tag
from django.urls import reverse_lazy

from account.models import Profile

from forum.models import Topic
from forum.tests.utils import create_object_with_perm_for_user as create


@tag('auth')
class AuthViewTestBase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='Josh', email='josh.mail@localhost.com')


class TestLoginView(AuthViewTestBase):
    def test_using_correct_template(self):
        response = self.client.get(reverse_lazy('account:login'))

        self.assertTemplateUsed(response, 'registration/login.html')

    def test_authenticated_user_is_redirected_to_topic_list(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse_lazy('account:login'))

        self.assertRedirects(response, reverse_lazy('forum:topic_list'))

    def test_can_login_after_post(self):
        self.user.set_password('123')
        self.user.save()

        self.client.post(reverse_lazy('account:login'), {'username': 'Josh', 'password': '123'})

        self.assertEquals(get_user(self.client), self.user)

    def test_user_can_login_by_email_after_post(self):
        self.user.set_password('123')
        self.user.save()

        self.client.post(reverse_lazy('account:login'), {'username': 'josh.mail@localhost.com', 'password': '123'})

        self.assertEquals(get_user(self.client), self.user)

    def test_redirect_to_next_query_url(self):
        topic = create(Topic, 'Test Topic' ,Group.objects.get(name='Everyone'))
        self.user.set_password('123')
        self.user.save()

        response = self.client.post(reverse_lazy('account:login'), {'username': 'Josh',
                                                               'password': '123',
                                                               'next': topic.get_absolute_url()})

        self.assertRedirects(response, topic.get_absolute_url())


class TestLogoutView(AuthViewTestBase):
    def test_redirect_to_logout_redirect_url(self):
        logout_redirect_url = reverse_lazy(settings.LOGOUT_REDIRECT_URL)
        self.client.force_login(self.user)

        response = self.client.get(reverse_lazy('account:logout'))

        self.assertRedirects(response, logout_redirect_url)

    def test_view_logout_user(self):
        self.client.force_login(self.user)
        self.assertTrue(get_user(self.client).is_authenticated)

        self.client.get('/account/logout/')
        self.assertTrue(get_user(self.client).is_anonymous)


class TestRegisterView(AuthViewTestBase):
    def test_using_correct_template(self):
        response = self.client.get(reverse_lazy('account:register'))

        self.assertTemplateUsed(response, 'account/register.html')

    def test_user_is_redirected_to_topic_list_if_user_is_authenticated(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse_lazy('account:register'))

        self.assertRedirects(response, reverse_lazy('forum:topic_list'))

    def test_create_user_if_data_is_correct(self):
        users_count_before_post = User.objects.count()

        self.client.post(reverse_lazy('account:register'), {'username': 'Mat',
                                                            'email': 'mat.email@example.com',
                                                            'password': '123',
                                                            'confirm_password': '123'})

        users_count_after_post = User.objects.count()

        self.assertTrue(users_count_before_post + 1 == users_count_after_post)

    def test_created_user_have_profile(self):
        self.client.post(reverse_lazy('account:register'), {'username': 'Mat',
                                                            'email': 'mat.email@example.com',
                                                            'password': '123',
                                                            'confirm_password': '123'})

        profile = Profile.objects.filter(user__username='Mat')
        self.assertTrue(profile.exists())

    def test_render_register_done_template_if_data_is_correct(self):
        response = self.client.post(reverse_lazy('account:register'), {'username': 'Mat',
                                                            'email': 'mat.email@example.com',
                                                            'password': '123',
                                                            'confirm_password': '123'})

        self.assertTemplateUsed(response, 'account/register_done.html')

    def test_fail_creation_if_passwords_not_same(self):
        users_count_before_post = User.objects.count()
        self.client.post(reverse_lazy('account:register'), {'username': 'Mat',
                                                            'email': 'mat.email@example.com',
                                                            'password': '123',
                                                            'confirm_password': '321'})
        users_count_after_post = User.objects.count()

        self.assertTrue(users_count_before_post == users_count_after_post)

    def test_fail_creation_if_email_is_used(self):
        users_count_before_post = User.objects.count()

        self.client.post(reverse_lazy('account:register'), {'username': 'Mat',
                                                            'email': 'josh.mail@localhost.com',
                                                            'password': '123',
                                                            'confirm_password': '123'})

        users_count_after_post = User.objects.count()

        self.assertTrue(users_count_before_post == users_count_after_post)
