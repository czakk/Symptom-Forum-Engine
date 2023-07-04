from django.test import TestCase
from django.contrib.auth.models import User, Group

from forum.models import Topic, Subtopic
from forum.tests.utils import create_object_with_perm_for_user


class TestViewBase(TestCase):
    def setUp(self) -> None:
        self.everyone = Group.objects.get(name='Everyone')
        self.guest = User.objects.get(username='AnonymousUser')

        self.moderator = User.objects.create(username='Moderator')
        self.moderators = Group.objects.create(name='Moderators')
        self.moderators.user_set.add(self.moderator)

        self.topic = create_object_with_perm_for_user(Topic, 'Topic number 1', self.everyone)


class TestTopicList(TestViewBase):
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


class TestTopic(TestViewBase):
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