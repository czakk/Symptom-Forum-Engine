from django import template

from forum.models import Subtopic

from guardian.shortcuts import get_objects_for_user


register = template.Library()

@register.simple_tag
def get_subtopics_for_user(user, topic):
    return get_objects_for_user(user, 'forum.view_subtopic', topic.subtopics.all())