from django.shortcuts import render
from .forms import LoginForm
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.authtoken.models import Token



class TokenGetView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'apitoken/get.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        token = Token.objects.get_or_create(user=self.request.user)[0]
        context['token'] = token
        return self.render_to_response(context)
        
        
        

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
    return HttpResponseRedirect(reverse("user:login"))