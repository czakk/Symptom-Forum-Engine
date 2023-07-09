from django.shortcuts import render, redirect

from account.forms import UserRegisterForm

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