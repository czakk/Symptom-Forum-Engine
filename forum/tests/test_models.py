from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.test import TestCase
from forum.models import Topic, Subtopic, Post

class TestTopic(TestCase):
    def test_set_slug_on_model_save(self):
        subject = Topic.objects.create(name='Test Slug 2')

        self.assertEquals(subject.slug, 'test-slug-2')

    def test_get_absolute_url(self):
        subject = Topic.objects.create(name='Test Slug 2')

        self.assertEquals(subject.get_absolute_url(), '/forum/test-slug-2/')

    def test_raise_exception_when_topic_name_already_exists(self):
        Topic.objects.create(name='Test')

        with self.assertRaises(ValidationError):
            Topic.objects.create(name='Test')



class TestSubtopic(TestCase):
    def setUp(self):
        self.topic = Topic.objects.create(name='Test')

    def test_raise_exception_if_name_not_unique_for_topic(self):
        Subtopic.objects.create(topic=self.topic, name='Subtopic')

        with self.assertRaises(ValidationError):
            Subtopic.objects.create(topic=self.topic, name='subtopic')


    def test_same_name_can_be_use_for_other_topic(self):
        Subtopic.objects.create(topic=self.topic, name='Subtopic')
        other_topic = Topic.objects.create(name='Test 2')
        Subtopic.objects.create(topic=other_topic, name='Subtopic')

        self.assertEquals(Subtopic.objects.first().name, 'Subtopic')

    def test_get_absolute_url(self):
        sub = Subtopic.objects.create(topic=self.topic, name='Subtopic')
        self.assertEquals(sub.get_absolute_url(), '/forum/test/subtopic/')


class TestPost(TestCase):
    def setUp(self):
        self.topic = Topic.objects.create(name='Test')
        self.subtopic = Subtopic.objects.create(name='Test Sub', topic=self.topic)
        self.author = User.objects.create(username='Mark')

    def test_same_name_can_be_use_for_other_subtopic(self):
        Post.objects.create(name='Post', subtopic=self.subtopic, author=self.author, text='test')

        other_subtopic = Subtopic.objects.create(name='Test Sub 2', topic=self.topic)
        other_post = Post.objects.create(name='Post', subtopic=other_subtopic, author=self.author, text='test')

        self.assertEquals(other_post.name, 'Post')

    def test_get_absolute_url(self):
        post = Post.objects.create(name='Post', subtopic=self.subtopic, author=self.author, text='test')

        self.assertEquals(post.get_absolute_url(), f'/forum/{post.subtopic.topic.slug}/{post.subtopic.slug}/'
                                                   f'{post.id}-{post.slug}/')