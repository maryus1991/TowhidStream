from django.urls import path
from django.conf import settings
from django.conf.urls import static
from .views import AuthView, LoginView, RegisterView, RootView


urlpatterns = [
    path("", RootView.as_view(), name="root-view"),
    path("auth/", AuthView.as_view(), name="auth-view"),
    path("auth/login/", LoginView.as_view(), name="login-view"),
    path("auth/register/", RegisterView.as_view(), name="register-view")
]


urlpatterns = urlpatterns + static.static(
    settings.STATIC_URL, document_root=settings.STATIC_ROOT
)

