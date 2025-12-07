from django.views.generic import ListView, TemplateView, RedirectView
from .models import User
from django.shortcuts import render, redirect
from .forms import LoginForm, RegistrationForm
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse_lazy
from django.contrib import messages

class AuthView(TemplateView):

    def get(self, request, *args, **kwargs):
        
        login_from = LoginForm(request.POST or None)
        register_form = RegistrationForm(request.POST or None)

        return render(request, 'login.html', {
            "login_from":login_from,
            "register_form":register_form
        })


class RegisterView(RedirectView):
    """for register a new user and redirect to stream page"""

    def get_redirect_url(self, *args, **kwargs):
        request = self.request
        register_form = RegistrationForm(request.POST or None)
        if register_form.is_valid():
            name = register_form.cleaned_data['name']
            username = register_form.cleaned_data['username']
            password = register_form.cleaned_data['password']
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username=username, password=password, first_name=name)
                private_code = user.get_private_code()
                return "/stream/?private_code=%s/" % private_code

            else:
                messages.error(request, "نام کاربری وارد شده در سامانه موجود می باشد ")
                return reverse_lazy('auth-view')

        else:
            messages.error(request, register_form.errors)
            return reverse_lazy('auth-view')



class LoginView(RedirectView):
    """for login a user and redirect to stream page"""

    def get_redirect_url(self, *args, **kwargs):
        request = self.request
        login_form = LoginForm(request.POST or None)
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None and user.is_active:
                login(request, user)
                private_code = user.get_private_code()
                return "/stream/?private_code=%s/" % private_code

            else:
                messages.error(request, "کاربر شما موجود نمیباشد")
                return reverse_lazy('auth-view')

        else:
            messages.error(request, login_form.errors)
            return reverse_lazy('auth-view')


class LogoutView(RedirectView):
    """for logout a user and redirect to main page"""

    def get_redirect_url(self, *args, **kwargs):
        logout(self.request)
        return reverse_lazy("root-view")



class RootView(ListView):
    pass
