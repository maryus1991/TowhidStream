from django.views.generic import ListView, TemplateView
from .models import User


class LoginView(TemplateView):

    def get(self, request, *args, **kwargs):
        pass

    def post(self, request, *args, **kwargs):
        pass

class LogoutView(TemplateView):
    pass

class RegisterView(TemplateView):
    def get(self, request, *args, **kwargs):
        pass

    def post(self, request, *args, **kwargs):
        pass

class RootView(ListView):
    pass
