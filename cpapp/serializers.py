from rest_framework import serializers
from .models import College, Course, Opportunity, Subject, CollegeCourse, CustomUser, UserWishCourse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = '__all__'

    def save(self):
        user = CustomUser(user_type=self.validated_data['user_type'],
                          email=self.validated_data['email'])
        password = self.validated_data['password']
        user.set_password(password)
        user.save()
        return user

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'


class OpportunitySerializer(serializers.ModelSerializer):
    course = serializers.SlugRelatedField(
        slug_field="uid",       
        queryset=Course.objects.all())

    class Meta:
        model = Opportunity
        fields = '__all__'


class SubjectSerializer(serializers.ModelSerializer):
    course = serializers.SlugRelatedField(
        slug_field="uid",        
        queryset=Course.objects.all())

    class Meta:
        model = Subject
        fields = '__all__'


class CollegeSerializer(serializers.ModelSerializer): 

    class Meta:
        model = College
        fields = '__all__'

class CollegeCourseSerializer(serializers.ModelSerializer): 
    college = serializers.SlugRelatedField(
        slug_field="name",        
        queryset=College.objects.all())

    course = serializers.SlugRelatedField(
        slug_field="uid",
        many=True,
        queryset=Course.objects.all())    

    class Meta:
        model = CollegeCourse
        fields = '__all__' 

class UserWishCourseSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field="email",
        queryset=CustomUser.objects.all())

    course = serializers.SlugRelatedField(
        slug_field="uid",
        many=True,
        queryset=Course.objects.all())    

    class Meta:
        model = UserWishCourse
        fields = '__all__' 

