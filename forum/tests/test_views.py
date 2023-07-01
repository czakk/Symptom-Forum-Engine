from django.test import TestCase
from django.contrib.auth.models import User, Group
from guardian.shortcuts import assign_perm
from forum.models import Topic, Subtopic


class TestTopicList(TestCase):
    def setUp(self):
        self.guest = User.objects.get(username='AnonymousUser')
        self.moderator = User.objects.create(username='Moderator')

        self.everyone = Group.objects.create(name='Everyone')
        self.moderators = Group.objects.create(name='Moderators')

        self.everyone.user_set.add(self.guest, self.moderator)
        self.moderators.user_set.add(self.moderator)

    def test_using_correct_template(self):
        response = self.client.get('/forum/')
        self.assertTemplateUsed(response, 'forum/topics/list.html')

    def test_if_there_is_no_one_topic_display_information(self):
        response = self.client.get('/forum/')
        self.assertContains(response, 'No topics')

    def test_guest_user_can_see_topics_for_everyone(self):
        assign_perm('forum.view_topic', self.everyone, Topic.objects.create(name='Topic number 1'))
        assign_perm('forum.view_topic', self.everyone, Topic.objects.create(name='Topic number 2'))

        response = self.client.get('/forum/')

        self.assertContains(response, 'Topic number 1')
        self.assertContains(response, 'Topic number 2')

    def test_guest_user_cant_see_topics_without_permission(self):
        assign_perm('forum.view_topic', self.everyone, Topic.objects.create(name='Topic number 1'))
        assign_perm('forum.view_topic', self.everyone, Topic.objects.create(name='Topic number 2'))
        Topic.objects.create(name='Topic number 3')

        response = self.client.get('/forum/')

        self.assertContains(response, 'Topic number 1')
        self.assertContains(response, 'Topic number 2')
        self.assertNotContains(response, 'Topic number 3')

    def test_user_from_other_group_can_see_topics_for_his_group_and_from_everyone_group(self):
        assign_perm('forum.view_topic', self.everyone, Topic.objects.create(name='Topic number 1'))
        assign_perm('forum.view_topic', self.everyone, Topic.objects.create(name='Topic number 2'))

        assign_perm('forum.view_topic', self.moderators, Topic.objects.create(name='Topic number 3'))

        self.client.force_login(user=self.moderator)
        response = self.client.get('/forum/')

        self.assertContains(response, 'Topic number 1')
        self.assertContains(response, 'Topic number 2')
        self.assertContains(response, 'Topic number 3')

    def test_user_can_see_subtopics_for_everyone(self):
        topic = Topic.objects.create(name='Topic number 1')
        assign_perm('forum.view_topic', self.everyone, topic)
        assign_perm('forum.view_subtopic', self.everyone, Subtopic.objects.create(topic=topic,
                                                                                  name='Subtopic number 1'))

        response = self.client.get('/forum/')

        self.assertContains(response, 'Topic number 1')
        self.assertContains(response, 'Subtopic number 1')

    def test_user_cant_see_subtopics_without_permission(self):
        topic = Topic.objects.create(name='Topic number 1')
        assign_perm('forum.view_topic', self.everyone, topic)
        assign_perm('forum.view_subtopic', self.everyone, Subtopic.objects.create(topic=topic,
                                                                                  name='Subtopic number 1'))
        Subtopic.objects.create(topic=topic, name='Subtopic number 2')

        response = self.client.get('/forum/')

        self.assertContains(response, 'Topic number 1')
        self.assertContains(response, 'Subtopic number 1')
        self.assertNotContains(response, 'Subtopic number 2')

    def test_user_can_see_subtopics_for_his_group(self):
        topic = Topic.objects.create(name='Topic number 1')
        assign_perm('forum.view_topic', self.everyone, topic)
        assign_perm('forum.view_subtopic', self.everyone, Subtopic.objects.create(topic=topic,
                                                                                  name='Subtopic number 1'))
        assign_perm('forum.view_subtopic', self.moderators, Subtopic.objects.create(topic=topic,
                                                                                  name='Subtopic number 2'))

        self.client.force_login(user=self.moderator)
        response = self.client.get('/forum/')

        self.assertContains(response, 'Topic number 1')
        self.assertContains(response, 'Subtopic number 1')
        self.assertContains(response, 'Subtopic number 2')
