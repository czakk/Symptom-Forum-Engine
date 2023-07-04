from django.contrib import admin
from forum.models import Topic, Subtopic, Post

# Register your models here.

class SubtopicInline(admin.StackedInline):
    model = Subtopic


class PostInline(admin.StackedInline):
    model = Post


class TopicAdminBase(admin.ModelAdmin):
    list_display = ('name', )
    prepopulated_fields = {'slug': ('name', )}
    search_fields = ('name', )


@admin.register(Topic)
class TopicAdmin(TopicAdminBase):
    inlines = (SubtopicInline, )


@admin.register(Subtopic)
class SubtopicAdmin(TopicAdminBase):
    inlines = (PostInline, )


@admin.register(Post)
class PostAdmin(TopicAdminBase):
    list_display = ('name', 'author', 'created', 'status', 'hidden', )
    list_filter = ('name', 'author', 'created', 'status', 'hidden', )
    search_fields = ('name', )
    prepopulated_fields = {'slug': ('name',)}
    raw_id_fields = ('author', )
