from django.shortcuts import render

from forum.models import Topic, Subtopic

from guardian.shortcuts import get_objects_for_user

# Create your views here.

def topic_list(request):
    topics = get_objects_for_user(request.user, 'forum.view_topic', Topic)
    subtopics = get_objects_for_user(request.user, 'forum.view_subtopic', Subtopic)
    return render(request,
                  'forum/topics/list.html',
                  {'topics': topics,
                   'subtopics': subtopics})

def topic(request):
    pass

def subtopic(request):
    pass