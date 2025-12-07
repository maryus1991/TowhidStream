from django.db import models
from django.utils.crypto import get_random_string
from django.contrib.auth.models import (
    AbstractUser,
    BaseUserManager,
    PermissionsMixin
)

class UserManager(BaseUserManager):
    """custom user manager """

    def _create_user(self, username, password, **extra_fields):
        """for create new user"""
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password, **extra_fields):
        """create new user"""
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        """create new superuser"""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self._create_user(username, password, **extra_fields)


class User(AbstractUser, PermissionsMixin):
    """create custom user model"""

    email = models.EmailField(
        unique=True,
        null=True,
        blank=True,
        max_length=255,
        verbose_name="ایمیل"
    )
    logo = models.ImageField(
        upload_to="avatars/",
        null=True,
        blank=True,
        max_length=255,
        verbose_name='لوگو'
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='توضیحات'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="اجازه به استریم"
    )
    is_stream=models.BooleanField(
        default=False,
        verbose_name="درحال استریم"
    )
    link_of_stream=models.CharField(
        verbose_name="لینک استریم",
        max_length=255,
        null=True,
        blank=True,
    )
    private_code=models.CharField(
        verbose_name="کد شناسایی"
        ,max_length=255,
        editable=False,
        null=True,
        blank=True,
    )

    def get_link_of_stream(self):
        link_of_stream = f"stream/{self.username}/{self.id}"
        if not self.link_of_stream :
            self.link_of_stream = link_of_stream
            self.save()
        return link_of_stream

    def get_private_code(self):
        code = get_random_string(length=255)
        self.private_code = code
        self.save()
        return code


    objects = UserManager()

    class Meta:
        verbose_name="کاربر"
        verbose_name_plural="کاربران"