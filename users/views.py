from django.shortcuts import render
from .forms import LoginForm
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib import messages


def login_view(request):
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                if request.GET:
                    next_url = request.GET.get("next")
                    if next_url:
                        return HttpResponseRedirect(next_url)
                return HttpResponseRedirect(reverse("home"))
            else:
                return HttpResponse("Your account is disabled.")
        else:
            messages.error(request, 'Login credentials are incorrect!')

    return render(request, 'users/login.html', locals())


def logout_view(request):
    user = request.user
    if not user.is_anonymous():
        logout(request)
    return HttpResponseRedirect(reverse("login"))