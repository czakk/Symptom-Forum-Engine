from django.urls import path
from . import views

app_name = 'forum'

urlpatterns = [
    path('', views.topic_list, name='topic_list'),
    path('<slug:topic_slug>/', views.topic_detail, name='topic_detail'),
    path('<slug:topic_slug>/<slug:subtopic_slug>/', views.subtopic_detail, name='subtopic_detail'),
    path('<slug:topic_slug>/<slug:subtopic_slug>/<int:post_id>-<slug:post_slug>/',
         views.post_detail, name='post_detail')
]