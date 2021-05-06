from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.db.models.signals import *
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import ugettext_lazy as _


class CustomAccountManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('The Email must be set')
        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email=self.normalize_email(email), password=password,)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser):
    student = 'Student'    
    college = 'College'
    admin = 'Admin'
    TYPE = ((college, college), (admin, admin),(student, student))    
    user_type = models.CharField(max_length=100, choices=TYPE, default=admin)
    username = models.CharField(max_length=55)
    email = models.EmailField(max_length=254, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomAccountManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

    def __int__(self):
        return self.id


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class Course(models.Model):
    """ Course Model """    
    uid = models.CharField(max_length=10, unique=True)
    level = models.CharField(max_length=50, null=True, blank=True)
    field = models.CharField(max_length=50, null=True, blank=True)
    stream = models.CharField(max_length=50, null=True, blank=True)
    course = models.CharField(max_length=200, null=True, blank=True)
    description = models.CharField(max_length=1000, null=True, blank=True)
    eligibility = models.CharField(max_length=100, null=True, blank=True)
    duration = models.CharField(max_length=200, null=True, blank=True)
    govt_recog = models.CharField(max_length=200, null=True, blank=True)

class Opportunity(models.Model):
    """ Opportunity Model """
    name = models.CharField(max_length=100, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

class Subject(models.Model):
    """ Subject Model """
    name = models.CharField(max_length=100, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

class College(models.Model):
    """ College Model """
    name = models.CharField(max_length=200, null=True, blank=True)
    URL = models.CharField(max_length=200, null=True, blank=True)
    password = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField(max_length = 254, unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=12, unique=True, null=True, blank=True)
    prospectus_link = models.CharField(max_length=200, null=True, blank=True)
    city =  models.CharField(max_length=50, null=True, blank=True)
    state =  models.CharField(max_length=50, null=True, blank=True)
    country =  models.CharField(max_length=50, null=True, blank=True)
    pin =  models.CharField(max_length=20, null=True, blank=True)    
    status = models.BooleanField(default=False)

class CollegeCourse(models.Model):
    id = models.AutoField(primary_key=True)
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    course = models.ManyToManyField(Course)

class UserWishCourse(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    course = models.ManyToManyField(Course)

