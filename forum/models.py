from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.core.exceptions import ValidationError

# Create your models here.

class TopicBase(models.Model):
    name = models.CharField(max_length=32)
    slug = models.SlugField()

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        self.full_clean()
        super().save(*args, **kwargs)


class Topic(TopicBase):
    class Meta:
        verbose_name = 'topic'
        verbose_name_plural = 'topics'

    def clean(self, *args, **kwargs):
        duplicate_topic = self.__class__.objects.filter(name=self.name)
        if duplicate_topic.exists():
            raise ValidationError('Topic with this name already exists')

    def get_absolute_url(self):
        return reverse('forum:topic', args=[self.slug])


class Subtopic(TopicBase):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE,
                              related_name='subtopics')

    class Meta:
        verbose_name = 'subtopic'
        verbose_name_plural = 'subtopics'

    def clean(self, *args, **kwargs):
        duplicate_subtopic = self.topic.subtopics.filter(name=self.name)
        if duplicate_subtopic.exists():
            raise ValidationError('Subtopic with this name already exists')

    def get_absolute_url(self):
        return reverse('forum:subtopic', args=[self.topic.slug,
                                               self.slug])