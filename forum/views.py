from django.http import HttpResponseNotFound
from django.shortcuts import render, get_object_or_404

from forum.models import Topic, Subtopic, Post

from guardian.decorators import permission_required_or_403
from guardian.shortcuts import get_objects_for_user


# Create your views here.

def topic_list(request):
    topics = get_objects_for_user(request.user,
                                  'forum.view_topic',
                                  Topic)

    return render(request,
                  'forum/topics/list.html',
                  {'topics': topics})

@permission_required_or_403('forum.view_topic', (Topic, 'slug', 'topic_slug'))
def topic_detail(request, topic_slug):
    topic = get_object_or_404(Topic,
                              slug=topic_slug)
    subtopics = get_objects_for_user(request.user,
                                     'forum.view_subtopic',
                                     topic.subtopics.all())

    return render(request,
                  'forum/topics/topic.html',
                  {'topic': topic,
                   'subtopics': subtopics})

@permission_required_or_403('forum.view_subtopic', (Subtopic, 'topic__slug', 'topic_slug', 'slug', 'subtopic_slug'))
def subtopic_detail(request, topic_slug, subtopic_slug):
    subtopic = get_object_or_404(Subtopic,
                                 topic__slug=topic_slug,
                                 slug=subtopic_slug)
    posts = subtopic.posts.select_related('author')

    public_posts = posts.filter(hidden=False,
                                status='published')

    user_pending_posts = None
    if request.user.is_authenticated:
        user_pending_posts = posts.filter(author=request.user,
                                          status='pending')

    return render(request,
                  'forum/topics/subtopic.html',
                  {'subtopic': subtopic,
                   'posts': public_posts,
                   'pending': user_pending_posts})

@permission_required_or_403('forum.view_subtopic', (Subtopic, 'topic__slug', 'topic_slug', 'slug', 'subtopic_slug'))
def post_detail(request, topic_slug, subtopic_slug, post_id, post_slug):
    post = get_object_or_404(Post,
                             subtopic__topic__slug=topic_slug,
                             subtopic__slug=subtopic_slug,
                             id=post_id,
                             slug=post_slug)

    if post.hidden:
        return HttpResponseNotFound()

    if post.status == 'pending' and post.author != request.user:
        return HttpResponseNotFound()

    return render(request,
                  'forum/topics/post.html',
                  {'post': post})