import datetime

from django.contrib.auth.models import User, Group
from django.test import TestCase
from django.utils import timezone

from forum.models import Topic, Subtopic, Post
from forum.tests.utils import create_object_with_perm_for_user

from unittest import mock


class ViewTestBase(TestCase):
    def setUp(self) -> None:
        self.everyone = Group.objects.get(name='Everyone')
        self.guest = User.objects.get(username='AnonymousUser')

        self.moderator = User.objects.create(username='Moderator')
        self.moderators = Group.objects.create(name='Moderators')
        self.moderators.user_set.add(self.moderator)

        self.topic = create_object_with_perm_for_user(Topic, 'Topic number 1', self.everyone)


class TestTopicList(ViewTestBase):
    def test_using_correct_template(self):

        response = self.client.get('/forum/')

        self.assertTemplateUsed(response, 'forum/topics/list.html')

    def test_if_there_is_no_one_topic_display_information(self):
        Topic.objects.first().delete()

        response = self.client.get('/forum/')

        self.assertContains(response, 'No topics')

    def test_guest_user_can_see_topics_for_everyone(self):
        create_object_with_perm_for_user(Topic, 'Topic number 2', self.everyone)

        response = self.client.get('/forum/')

        self.assertContains(response, 'Topic number 1')
        self.assertContains(response, 'Topic number 2')

    def test_guest_user_cant_see_topics_without_permission(self):
        create_object_with_perm_for_user(Topic, 'Topic number 2', self.everyone)
        Topic.objects.create(name='Topic number 3')

        response = self.client.get('/forum/')

        self.assertContains(response, 'Topic number 1')
        self.assertContains(response, 'Topic number 2')
        self.assertNotContains(response, 'Topic number 3')

    def test_user_from_other_group_can_see_topics_for_his_group_and_from_everyone_group(self):
        create_object_with_perm_for_user(Topic, 'Topic number 2', self.everyone)
        create_object_with_perm_for_user(Topic, 'Topic number 3', self.moderators)

        self.client.force_login(user=self.moderator)
        response = self.client.get('/forum/')

        self.assertContains(response, 'Topic number 1')
        self.assertContains(response, 'Topic number 2')
        self.assertContains(response, 'Topic number 3')

    def test_user_can_see_subtopics_for_everyone(self):
        create_object_with_perm_for_user(Subtopic, 'Subtopic number 1', self.everyone, topic=self.topic)

        response = self.client.get('/forum/')

        self.assertContains(response, 'Topic number 1')
        self.assertContains(response, 'Subtopic number 1')

    def test_user_cant_see_subtopics_without_permission(self):
        create_object_with_perm_for_user(Subtopic, 'Subtopic number 1', self.everyone, topic=self.topic)
        Subtopic.objects.create(topic=self.topic, name='Subtopic number 2')

        response = self.client.get('/forum/')

        self.assertContains(response, 'Topic number 1')
        self.assertContains(response, 'Subtopic number 1')
        self.assertNotContains(response, 'Subtopic number 2')

    def test_user_can_see_subtopics_for_his_group(self):
        create_object_with_perm_for_user(Subtopic, 'Subtopic number 1', self.everyone, topic=self.topic)
        create_object_with_perm_for_user(Subtopic, 'Subtopic number 2', self.everyone, topic=self.topic)

        self.client.force_login(user=self.moderator)
        response = self.client.get('/forum/')

        self.assertContains(response, 'Topic number 1')
        self.assertContains(response, 'Subtopic number 1')
        self.assertContains(response, 'Subtopic number 2')


class TestTopic(ViewTestBase):
    def test_view_using_correct_template(self):
        response = self.client.get(self.topic.get_absolute_url())

        self.assertTemplateUsed(response, 'forum/topics/topic.html')

    def test_view_display_topic_name(self):
        response = self.client.get(self.topic.get_absolute_url())

        self.assertContains(response, self.topic.name)

    def test_view_display_subtopics(self):
        create_object_with_perm_for_user(Subtopic, 'Sub 1', self.everyone, topic=self.topic)
        create_object_with_perm_for_user(Subtopic, 'Sub 2', self.everyone, topic=self.topic)

        response = self.client.get(self.topic.get_absolute_url())

        self.assertContains(response, 'Sub 1')
        self.assertContains(response, 'Sub 2')

    def test_view_display_subtopics_available_for_user(self):
        create_object_with_perm_for_user(Subtopic, 'Sub 1', self.everyone, topic=self.topic)
        create_object_with_perm_for_user(Subtopic, 'Sub 2', self.everyone, topic=self.topic)
        create_object_with_perm_for_user(Subtopic, 'Sub 3', self.moderators, topic=self.topic)

        response = self.client.get(self.topic.get_absolute_url())

        self.assertContains(response, 'Sub 1')
        self.assertContains(response, 'Sub 2')
        self.assertNotContains(response, 'Sub 3')

        self.client.force_login(self.moderator)
        response = self.client.get(self.topic.get_absolute_url())

        self.assertContains(response, 'Sub 1')
        self.assertContains(response, 'Sub 2')
        self.assertContains(response, 'Sub 3')

    def test_view_return_403_if_user_dont_have_permission(self):
        topic = create_object_with_perm_for_user(Topic, 'Topic number 2', self.moderators)

        response = self.client.get(topic.get_absolute_url())

        self.assertEquals(response.status_code, 403)

    def test_view_return_404_if_topic_does_not_exists(self):
        response = self.client.get('/forum/topic-number-2/')

        self.assertEqual(response.status_code, 404)


class TestSubtopic(ViewTestBase):
    def setUp(self):
        super().setUp()
        self.subtopic = create_object_with_perm_for_user(Subtopic, 'Subtopic number 1', self.everyone, topic=self.topic)
        self.user = User.objects.create(username='Josh')

    def test_view_using_correct_template(self):
        response = self.client.get(self.subtopic.get_absolute_url())

        self.assertTemplateUsed(response, 'forum/topics/subtopic.html')

    def test_view_display_information_about_no_posts(self):
        response = self.client.get(self.subtopic.get_absolute_url())

        self.assertContains(response, 'No posts')

    def test_view_display_subtopic_name(self):
        response = self.client.get(self.subtopic.get_absolute_url())

        self.assertContains(response, self.subtopic.name)

    def test_view_display_all_posts(self):
        Post.objects.create(author=self.user, subtopic=self.subtopic, name='Post number 1', text='nothing')
        Post.objects.create(author=self.user, subtopic=self.subtopic, name='Post number 2', text='nothing')
        Post.objects.create(author=self.user, subtopic=self.subtopic, name='Post number 3', text='nothing')

        response = self.client.get(self.subtopic.get_absolute_url())

        self.assertContains(response, 'Post number 1')
        self.assertContains(response, 'Post number 2')
        self.assertContains(response, 'Post number 3')

    def test_view_display_only_published_and_no_hidden_posts(self):
        Post.objects.create(author=self.user, subtopic=self.subtopic, name='Post number 1', text='nothing')
        Post.objects.create(author=self.user, subtopic=self.subtopic, name='Post number 2', text='nothing', hidden=True)
        Post.objects.create(author=self.user, subtopic=self.subtopic, name='Post number 3', text='nothing',
                            status='pending')

        response = self.client.get(self.subtopic.get_absolute_url())

        self.assertContains(response, 'Post number 1')
        self.assertNotContains(response, 'Post number 2')
        self.assertNotContains(response, 'Post number 3')

    def test_author_can_see_his_pending_post(self):
        Post.objects.create(author=self.user, subtopic=self.subtopic, name='Post number 1', text='nothing',
                            status='pending')

        self.client.force_login(self.user)
        response = self.client.get(self.subtopic.get_absolute_url())

        self.assertContains(response, 'Post number 1')

    def test_view_raise_403_if_user_doesnt_have_permissions(self):
        other_subtopic = create_object_with_perm_for_user(Subtopic, 'Other Subtopic', self.moderators, topic=self.topic)

        response = self.client.get(other_subtopic.get_absolute_url())

        self.assertEquals(response.status_code, 403)

    def test_view_raise_404_if_subject_doesnt_exists(self):
        response = self.client.get(f'/forum/{self.topic.slug}/no-subtopic-2/')

        self.assertEquals(response.status_code, 404)


class TestPostView(ViewTestBase):
    def setUp(self):
        super().setUp()
        self.subtopic = create_object_with_perm_for_user(Subtopic, 'Subtopic number 1', self.everyone, topic=self.topic)
        self.user = User.objects.create(username='Josh')
        self.post = Post.objects.create(subtopic=self.subtopic, author=self.user, name='Post number 1', text='Test')

    def test_post_detail_using_correct_template(self):
        response = self.client.get(self.post.get_absolute_url())

        self.assertTemplateUsed(response, 'forum/topics/post.html')

    def test_view_display_post_content(self):
        response = self.client.get(self.post.get_absolute_url())

        self.assertContains(response, self.post.name)
        self.assertContains(response, self.post.author.username)
        # DD/MM/YYYY HH:mm - datetime format for created and updated
        self.assertContains(response, self.post.created.strftime('%d/%m/%Y %H:%M'))
        self.assertContains(response, self.post.text)

    def test_view_display_updated_time_only_when_post_was_updated(self):
        response = self.client.get(self.post.get_absolute_url())

        self.assertNotContains(response, f'Updated at: {self.post.updated.strftime("%d/%m/%Y %H:%M")}')

        with mock.patch('django.utils.timezone.now', return_value=timezone.now() + datetime.timedelta(seconds=60)):
            self.post.save()

        response = self.client.get(self.post.get_absolute_url())

        self.assertContains(response, f'Updated at: {self.post.updated.strftime("%d/%m/%Y %H:%M")}')

    def test_view_raise_403_if_user_doesnt_have_permission_to_view_subtopic(self):
        other_subtopic = create_object_with_perm_for_user(Subtopic, 'Subtopic number 2', self.moderators, topic=self.topic)
        other_post = Post.objects.create(subtopic=other_subtopic, author=self.moderator, name='Post number 2', text='Text')

        response = self.client.get(other_post.get_absolute_url())

        self.assertEquals(response.status_code, 403)

    def test_view_raise_404_if_post_doesnt_exists(self):
        response = self.client.get(f'/forum/{self.topic.slug}/{self.subtopic.slug}/500-post-number-3/')

        self.assertEquals(response.status_code, 404)

    def test_user_cant_access_view_if_post_is_hidden(self):
        hidden_post = Post.objects.create(subtopic=self.subtopic, author=self.user, name='Hidden Post', text='Text',
                                          hidden=True)

        response = self.client.get(hidden_post.get_absolute_url())

        self.assertEquals(response.status_code, 404)

    def test_user_can_access_to_detail_pending_post_if_he_is_an_author(self):
        pending_post = Post.objects.create(subtopic=self.subtopic, author=self.user, name='Hidden Post', text='Text',
                                          status='pending')

        self.client.force_login(self.user)
        response = self.client.get(pending_post.get_absolute_url())

        self.assertEquals(response.status_code, 200)

    def test_other_users_cant_access_pending_post(self):
        pending_post = Post.objects.create(subtopic=self.subtopic, author=self.user, name='Hidden Post', text='Text',
                                          status='pending')

        response = self.client.get(pending_post.get_absolute_url())

        self.assertEquals(response.status_code, 404)