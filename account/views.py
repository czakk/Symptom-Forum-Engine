from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404

from account.forms import UserRegisterForm
from forum.models import Subtopic, Post
from guardian.shortcuts import get_objects_for_user

# Create your views here.

def register(request):
    if request.user.is_authenticated:
        return redirect('forum:topic_list')

    if request.method == 'POST':
        form = UserRegisterForm(data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            new_user = form.save(commit=False)
            new_user.set_password(cd['password'])
            new_user.save()

            return render(request, 'account/register_done.html')
    else:
        form = UserRegisterForm()

    return render(request,
                  'account/register.html',
                  {'form': form})

def user_detail(request, username):
    user = get_object_or_404(User,
                             username=username)
    subtopics = get_objects_for_user(request.user,
                                     'forum.view_subtopic',
                                     Subtopic)
    posts = Post.objects.filter(subtopic__in=subtopics,
                                author=user.id)

    return render(request,
                  'account/user_detail.html',
                  {'user': user,
                   'posts': posts})

def profile_edit(request):
    pass