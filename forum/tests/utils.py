from forum.models import Topic, Subtopic

from guardian.shortcuts import assign_perm


def create_object_with_perm_for_user(model, name, user_or_group, **kwargs):
    obj = model.objects.create(name=name, **kwargs)
    assign_perm(f'forum.view_{model.__name__.lower()}', user_or_group, obj)
    return obj