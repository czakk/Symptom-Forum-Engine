import datetime

from django.contrib.auth.models import User, Group
from django.test import TestCase
from django.urls import reverse_lazy

from forum.models import Topic, Subtopic, Post
from forum.tests.utils import create_object_with_perm_for_user


class TestUserProfile(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='Pat')
        self.view = reverse_lazy('account:user_detail', args=[self.user.username])

    def test_user_detail_return_view(self):
        response = self.client.get(self.view)

        self.assertEquals(response.status_code, 200)

    def test_using_correct_template(self):
        response = self.client.get(self.view)

        self.assertTemplateUsed(response, 'account/user_detail.html')

    def test_view_display_information_about_user(self):
        self.user.profile.birthday = datetime.date(2023, 7, 10)
        self.user.profile.save()

        response = self.client.get(self.view)

        self.assertContains(response, self.user.username)
        # Format DD/MM/YYYY
        self.assertContains(response, self.user.profile.birthday.strftime('%d/%m/%Y'))

    def test_only_owner_of_profile_has_link_to_edit_profile(self):
        response = self.client.get(self.view)
        self.assertNotContains(response, 'Edit profile')

        self.client.force_login(self.user)
        response = self.client.get(self.view)

        self.assertContains(response, 'Edit profile')

    def test_display_visitor_only_this_posts_created_by_profile_owner_which_visitor_have_perms(self):
        other_user = User.objects.create(username='Other')
        everyone = Group.objects.get(name='Everyone')
        admins = Group.objects.get(name='Admins')
        self.user.groups.add(admins)

        topic_everyone = create_object_with_perm_for_user(Topic, 'Topic num 1', everyone)
        topic_other = create_object_with_perm_for_user(Topic, 'Topic num 2', other_user)

        subtopic_everyone = create_object_with_perm_for_user(Subtopic, 'Sub num 1', everyone, topic=topic_everyone)
        subtopic_admins = create_object_with_perm_for_user(Subtopic, 'Sub num 2', admins, topic=topic_everyone)
        subtopic_other = create_object_with_perm_for_user(Subtopic, 'Sub num 3', other_user, topic=topic_other)


        Post.objects.create(author=self.user,
                            subtopic=subtopic_everyone,
                            name='Post num 1',
                            text='test')
        Post.objects.create(author=other_user,
                            subtopic=subtopic_everyone,
                            name='Other post',
                            text='test')
        Post.objects.create(author=self.user,
                            subtopic=subtopic_admins,
                            name='Post num 2',
                            text='test')

        Post.objects.create(author=self.user,
                            subtopic=subtopic_other,
                            name='Post num 3',
                            text='test')

        response = self.client.get(self.view)

        self.assertContains(response, 'Post num 1')
        self.assertNotContains(response, 'Other post')
        self.assertNotContains(response, 'Post num 2')
        self.assertNotContains(response, 'Post num 3')

        self.client.force_login(self.user)

        response = self.client.get(self.view)

        self.assertContains(response, 'Post num 1')
        self.assertNotContains(response, 'Other post')
        self.assertContains(response, 'Post num 2')
        self.assertNotContains(response, 'Post num 3')

    def test_raise_404_error_if_user_doesnt_exists(self):
        response = self.client.get('/account/profile/mat/')

        self.assertEquals(response.status_code, 404)
