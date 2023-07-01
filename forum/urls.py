from django.urls import path
from . import views

app_name = 'forum'

urlpatterns = [
    path('', views.topic_list, name='topic_list'),
    path('<slug:topic>/', views.topic, name='topic'),
    path('<slug:topic>/<slug:subtopic>/', views.subtopic, name='subtopic')
]