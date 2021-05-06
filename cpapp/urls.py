from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from . import views

urlpatterns = [
    # Based on Django viewsets, these are not customized
    path('coursesList/', views.CoursesList.as_view(), name="courses"),
    path('opportunitiesList/', views.OpportunitiesList.as_view(), name="opportunities"),
    path('subjectsList/', views.SubjectsList.as_view(), name="subjects"),
    path('collegesList/', views.CollegesList.as_view(), name="colleges"),
    path('collegecourseList/', views.CollegeCourseList.as_view(), name="college_courses"),
    path('usersList/', views.UsersList.as_view(), name="users"),
     path('userswishList/', views.UsersWishList.as_view(), name="user_wishes"),
    # customized data urls courses based    
    path('courses/<str:level>/', views.courses_data, name="courses_data"),    
    path('courses_colleges/<str:level>/', views.courses_with_colleges, name="courses_colleges"),    
    path('search_courses/', views.seach_bar_data, name="search_bar"),
    path('user_wish_courses/', views.user_wish_courses, name="user_wishes"),
    # customized data urls colleges based
    path('college_registration/', views.CollegeRegistration.as_view(), name="college_registration"),
    path('college_login/', views.college_login, name="college_login"),
    path('update_college_details/', views.update_college_details, name="college_update"),
    path('college_courses/', views.college_with_courses, name="college_courses"),   
    path('user_details/', views.get_user_deatils, name="user_details"),
    path('data_corrections/', views.data_corrections, name="data_corrections"),
    # path('user_registration/', views.UserRegistration.as_view(), name="user_registration"),
    # path('update_user_details/', views.update_user_details, name="user_update"),    

    
]
