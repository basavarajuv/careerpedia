from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from rest_framework import generics, status
from django.contrib.auth import get_user_model
from django.http import JsonResponse, HttpResponse
from rest_framework.response import Response
from django.db.models import Q
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.contrib import messages
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth.password_validation import validate_password

from rest_framework.status import (HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_200_OK)
from .serializers import (CourseSerializer, CollegeSerializer, OpportunitySerializer,
                          SubjectSerializer, CollegeCourseSerializer, UserSerializer,
                          UserWishCourseSerializer)
from .models import (Course, College, Subject, Opportunity, CollegeCourse, CustomUser, UserWishCourse)

HOST_EMAIL = settings.EMAIL_HOST_USER


@permission_classes((IsAuthenticated,))
@api_view(['GET'])
def get_user_deatils(request):
    user_data = {}
    try:
        user = request.user    
        user_data["email"] = user.email
        user_data["user_type"] = user.user_type
        user_data["username"] = user.username
        user_data["is_active"] = user.is_active
    except:
        user_data["error"] = "Error in getting user details"
    return JsonResponse(user_data, status=status.HTTP_200_OK)


@api_view(["POST"])
def college_login(request):
    email = request.data.get("email")
    password = request.data.get("password")
    if email is None or password is None:
        return Response({'error': 'Please provide both email and password'},
                        status=HTTP_400_BAD_REQUEST)
    user = authenticate(email=email, password=password)
    if not user:
        return Response({'error': 'Invalid Credentials'}, status=HTTP_404_NOT_FOUND)
    user_type = user.user_type
    if user_type != "College":
        return Response({'error': 'Invalid type registration'}, status=HTTP_404_NOT_FOUND)
    login(request, user)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key}, status=HTTP_200_OK)


class UsersList(generics.ListCreateAPIView):
    """ Returns the Courses List, can also help to add new course"""
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


class UsersWishList(generics.ListCreateAPIView):
    """ Returns the users wish List, can also help to add new wish"""
    queryset = UserWishCourse.objects.all()
    serializer_class = UserWishCourseSerializer


class CoursesList(generics.ListCreateAPIView):
    """ Returns the Courses List, can also help to add new course"""
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class SubjectsList(generics.ListCreateAPIView):
    """ Returns the Subjects List, can also help to add new subject"""
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer


class OpportunitiesList(generics.ListCreateAPIView):
    """ Returns the Opportunitities List, can also help to add new opportunity"""
    queryset = Opportunity.objects.all()
    serializer_class = OpportunitySerializer


class CollegesList(generics.ListCreateAPIView):
    """ Returns the college List, can also help to add new colleges"""
    queryset = College.objects.all()
    serializer_class = CollegeSerializer


class CollegeCourseList(generics.ListCreateAPIView):
    """ Returns the college List, can also help to add new colleges"""
    queryset = CollegeCourse.objects.all()
    serializer_class = CollegeCourseSerializer


def get_cc_data(course_obj):
    ser_course = CourseSerializer(course_obj)
    opps = Opportunity.objects.filter(course=course_obj).values_list('name', flat=True)
    subjs = Subject.objects.filter(course=course_obj).values_list('name', flat=True)
    college_objs = CollegeCourse.objects.filter(course=course_obj)
    ret_data = ser_course.data
    if str(ret_data["field"]) == "nan":
        ret_data["field"] = ""

    ret_data["opportunities"] = list(opps)
    ret_data["subjects"] = list(subjs)
    ret_data["colleges"] = []
    for colg in college_objs:
        ac_colg = College.objects.get(name=colg.college.name)
        col_ser = CollegeSerializer(ac_colg)
        col_data = col_ser.data
        if col_data["status"]:            
            del col_data['id']
            del col_data['password']
            ret_data["colleges"].append(col_data)
    return ret_data    

def get_query_params_data(q_vals, level):
    cat_course_objs = []
    if q_vals:
        s_level = q_vals.get("field", None)
        st_val = q_vals.get("stream", None)
        if s_level is not None and st_val is not None:
                cat_course_objs = Course.objects.filter(Q(level=level) & Q(field=s_level) & Q(stream=st_val))
        elif s_level is not None:
                cat_course_objs = Course.objects.filter(Q(level=level) & Q(field=s_level))
        elif st_val is not None:
            cat_course_objs = Course.objects.filter(Q(level=level) & Q(stream=st_val))
        else:
            cat_course_objs = Course.objects.filter(level=level)
    else:
        cat_course_objs = Course.objects.filter(level=level)
    return cat_course_objs


@api_view(['GET'])
def courses_data(request, level):
    """ This will return courses data. level info is mandatory"""
    try:
        q_vals = request.query_params.dict()    
        if request.method == 'GET':
            cat_course_objs = get_query_params_data(q_vals, level)
            json_data = []
            for cr_val in cat_course_objs:
                ser_course = CourseSerializer(cr_val)
                cr_data = ser_course.data                
                json_data.append({"uid":cr_data['uid'], "course":cr_data['course']})
            return JsonResponse(json_data, safe=False)
        else:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
    except Exception as err:
        error_dict = {"error": str(err)}
        return JsonResponse(error_dict, safe=False)


@api_view(['GET'])
def courses_with_colleges(request, level):
    """ This will return courses with colleges data. level info is mandatory"""
    try:
        q_vals = request.query_params.dict()    
        if request.method == 'GET':
            cat_course_objs = get_query_params_data(q_vals, level)
            json_data = []
            for cr_val in cat_course_objs:
                cr_data = get_cc_data(cr_val)
                json_data.append(cr_data)
            return JsonResponse(json_data, safe=False)
        else:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
    except Exception as err:
        error_dict = {"error": str(err)}
        return JsonResponse(error_dict, safe=False)


def make_course_data(req_data, ext_course=None):
    new_req_data = {}
    if "college" in req_data:
        new_req_data["college"] = req_data["college"]
    if ext_course is not None:
        new_req_data["course"] = ext_course
    else:
        new_req_data["course"] = []
    if "courses" in req_data:
        for item in req_data["courses"]:
            if item["checkbox"]:
                new_req_data["course"].append(item["uid"])
            else:
                 new_req_data["course"].remove(item["uid"])
    return new_req_data


@permission_classes((IsAuthenticated,))
@api_view(['GET', 'POST'])
def college_with_courses(request):
    try:
        if request.method == 'GET':
            q_vals = request.query_params.dict()
            college_name = q_vals.get("email", None)
            level = q_vals.get("level", None)
            try:
                col_course = CollegeCourse.objects.get(college__email=college_name)
            except CollegeCourse.DoesNotExist:       
                return HttpResponse(status=status.HTTP_404_NOT_FOUND)
            college_course_ser = CollegeCourseSerializer(col_course)
            college_course_data = college_course_ser.data                
            cat_course_objs = get_query_params_data(q_vals, level)       
            result = {"college":college_course_data["college"]}
            course_lst = []
            for cr_val in cat_course_objs:
                opps = Opportunity.objects.filter(course=cr_val).values_list('name', flat=True)
                cr_ser = CourseSerializer(cr_val)                
                cr_data = cr_ser.data
                cr_data["opportunities"] = list(opps)
                if cr_data['uid'] in college_course_data['course']:
                    cr_data["checkbox"] = True
                else:
                    cr_data["checkbox"] = False
                course_lst.append(cr_data)
            result["courses"] = course_lst  
            return JsonResponse(result, safe=False)
        elif request.method == 'POST':
            req_data = request.data
            if "email" in req_data:
                col_course_objs = CollegeCourse.objects.filter(college__email=req_data["email"])                
                if col_course_objs:
                    col_course = col_course_objs[0]
                    col_course_ser = CollegeCourseSerializer(col_course)
                    col_cour_data = col_course_ser.data
                    new_req_data = make_course_data(req_data, col_cour_data['course'])
                    serializer = CollegeCourseSerializer(col_course, data=new_req_data)
                else:
                    new_req_data = make_course_data(req_data)
                    serializer = CollegeCourseSerializer(data=new_req_data)               
                if serializer.is_valid():
                    serializer.save()
                    return JsonResponse(serializer.data, status=status.HTTP_202_ACCEPTED)
                else:
                    print(serializer.errors)
                    return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as err:
        error_dict = {"error": str(err)}
        return JsonResponse(error_dict, safe=False)


@permission_classes((IsAuthenticated,))
@api_view(['POST'])
def data_corrections(request):
    try:
        req_data = request.data
        user = request.user
        if request.method == 'POST':
            to_email = []           
            mail_subject = 'Reg: Data Corrections'
            submit_email = str(user.email)
            to_email.append(HOST_EMAIL)
            course_str = " Course UID: {} and Course Name: {}".format(req_data['uid'], req_data['course'])
            correction_str = "Correction Details are: {}".format(req_data['correction'])
            thanks_str = "Thanks,\nSubmitted by {}".format(submit_email)
            message = "Hi,\nPlease correct the data for the {}.\n{}.\n{}".format(course_str, correction_str, thanks_str)
            send_mail(mail_subject, message, HOST_EMAIL, to_email, fail_silently=False)
            return JsonResponse({"Success":"Sent data Correction email"}, safe=False)
        else:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
    except Exception as err:
        error_dict = {"error": str(err)}
        return JsonResponse(error_dict, safe=False)


@api_view(['POST'])
def seach_bar_data(request):
    try:
        req_data = request.data
        if request.method == 'POST':
            s_key = req_data["search_key"]
            cat_course_objs = Course.objects.filter(Q(course__contains=s_key))
            json_data = []
            for cr_val in cat_course_objs:
                cr_data = get_cc_data(cr_val)
                json_data.append(cr_data)
            return JsonResponse(json_data, safe=False)
        else:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
    except Exception as err:
        error_dict = {"error": str(err)}
        return JsonResponse(error_dict, safe=False)


def save_user_from_college(req_data):
    user_data = {}
    user_lst = ["name", "password", "email"]
    for item in user_lst:
        if item == "name":
            user_data["username"] = req_data[item].replace(" ", "")
        else:
            user_data[item] = req_data[item]
    user_data["user_type"] = "College"
    u_ser = UserSerializer(data=user_data)
    res_dict = {}
    if u_ser.is_valid():
        u_ser.save()
        res_dict["Success"] =  u_ser.data   
    else:
        res_dict["Error"] =  u_ser.errors
        print(u_ser.errors)
    return res_dict


class CollegeRegistration(APIView):
    def post(self, request, format=None):
        try:
            to_email = []
            req_data = request.data
            user_res = save_user_from_college(req_data)
            if "Error" not in user_res:
                col_cour_ser = CollegeSerializer(data=req_data)
                data = {}
                if col_cour_ser.is_valid():
                    college = col_cour_ser.save()
                    col_email = str(college.email)
                    data['response'] = "Successfully registered a new College"
                    data['email'] = col_email
                    mail_subject = 'College Email Confirmation'                    
                    to_email.append(col_email)
                    message = ("Hi, \nWelcome to the CareerPedia Platform (https://www.careerpedia.co/)."
                               "\nYour college has been Successfully Registered. Please Start listing the offered Courses."
                               "\nThank You, \n CareerPedia Team.")
                    send_mail(mail_subject, message, HOST_EMAIL, to_email, fail_silently=False,)
                else:
                    data = col_cour_ser.errors
                return Response(data)
            else:
                return JsonResponse(user_res, safe=False)
        except Exception as err:
            error_dict = {"error": str(err)}
            return JsonResponse(error_dict, safe=False)

def collge_reset_password(req_data):
    res_dict = {}
    try:
        user_objs = CustomUser.objects.filter(email=req_data["email"])
        if user_objs:
            user = user_objs[0]
            u_ser = UserSerializer(user, data=req_data)            
            if u_ser.is_valid():
                user.set_password(req_data["password"])
                user.save()                
                res_dict["Success"] =  user.email
            else:
                print(u_ser.errors)
                res_dict["Error"] =  u_ser.errors
        else:
            res_dict["Error"] =  "Not any college Account exists"
    except Exception as err:
        res_dict["Error"] = "Error occured in reset college password"
    return res_dict


@csrf_exempt
@permission_classes((IsAuthenticated,))
@api_view(['POST'])
def update_college_details(request):
    """ For updating college Details.."""
    try:
        req_data = request.data
        if "email" not in req_data:
            user = request.user
            if request.method == 'POST':
                to_email = [str(user.email)]            
                if "name" in req_data:
                    college_objs = College.objects.filter(name=req_data["name"])
                    if college_objs:
                        college = college_objs[0]
                        col_serializer = CollegeSerializer(college, data=req_data)
                        if col_serializer.is_valid():
                            if "password" in req_data:
                                auth_data = {}
                                auth_data["username"] = req_data["name"].replace(" ", "") 
                                auth_data["email"] = user.email
                                auth_data["password"] = req_data["password"]
                                auth_data["user_type"] = "College"
                                result = collge_reset_password(auth_data)                                
                                if "Error" not in result:
                                    col_serializer.save()
                                    mail_subject = 'College Account Reset Password Successful'                                    
                                    message = ("Hi, \nThis is the notification from the CarrerPedia Platform (https://www.careerpedia.co/)."
                                                "\nYour College Account password has been reset Successfully."
                                                "\nThank You, \n CareerPedia Team.")
                                    send_mail(mail_subject, message, HOST_EMAIL, to_email, fail_silently=False,)
                                    return JsonResponse(col_serializer.data, status=status.HTTP_202_ACCEPTED)
                                else:
                                    return JsonResponse(result, ssafe=False)
                            else:
                                col_serializer.save()
                                mail_subject = 'College Account Details Updated Successfully'                                    
                                message = ("Hi, \nThis is the notification from the CarrerPedia Platform (https://www.careerpedia.co/)."
                                            "\nYour College Account details have been updated Successfully."
                                            "\nThank You, \n CareerPedia Team.")
                                send_mail(mail_subject, message, HOST_EMAIL, to_email, fail_silently=False,)        
                                return JsonResponse(col_serializer.data, status=status.HTTP_202_ACCEPTED)   
                        else:
                            print(col_serializer.errors)
                            return JsonResponse(col_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        error_dict = {"error": "No College exists with the provided details"}
                        return JsonResponse(error_dict, safe=False)
            else:
                return HttpResponse(status=status.HTTP_404_NOT_FOUND)
        else:
            error_dict = {"error": "Please Remove email field from data, as it should not be changed"}
            return JsonResponse(error_dict, safe=False)
    except Exception as err:
        error_dict = {"error": str(err)}
        return JsonResponse(error_dict, safe=False)


def make_wish_course_data(req_data, ext_course=None):
    new_req_data = {}
    if "user" in req_data:
        new_req_data["user"] = req_data["user"]
    if ext_course is not None:
        new_req_data["course"] = ext_course
    else:
        new_req_data["course"] = []
    if "courses" in req_data:
        for item in req_data["courses"]:
            if item["wish"]:
                new_req_data["course"].append(item["uid"])
            else:
                 new_req_data["course"].remove(item["uid"])
    return new_req_data


@permission_classes((IsAuthenticated,))
@api_view(['GET', 'POST'])
def user_wish_courses(request):
    """ For getting and updating user wishLsit"""
    try:
        user = request.user
        c_user = CustomUser.objects.get(email=user.email)
        if request.method == 'GET':
            result = {}
            try:
                c_user_wish = UserWishCourse.objects.get(user=c_user)  
            except UserWishCourse.DoesNotExist:       
                return HttpResponse(status=status.HTTP_404_NOT_FOUND)           
            uw_ser = UserWishCourseSerializer(c_user_wish)
            ser_data = uw_ser.data
            wish_courses = ser_data["course"]
            result["courses"] = []
            for item in wish_courses:
                result["courses"].append({"uid": item, "wish": True})
            return JsonResponse(result, safe=False)
        elif request.method == 'POST':
            req_data = request.data
            req_data["user"] = user.email
            c_user_objs = UserWishCourse.objects.filter(user=c_user)
            if c_user_objs:
                c_user_obj = c_user_objs[0]
                uw_ser = UserWishCourseSerializer(c_user_obj)
                uw_ser_data = uw_ser.data
                new_req_data = make_wish_course_data(req_data, uw_ser_data['course'])
                uw_serializer = UserWishCourseSerializer(c_user_obj, data=new_req_data)
            else:
                new_req_data = make_wish_course_data(req_data)
                uw_serializer = UserWishCourseSerializer(data=new_req_data)

            if uw_serializer.is_valid():
                uw_serializer.save()
                return JsonResponse(uw_serializer.data, status=status.HTTP_202_ACCEPTED)
            else:
                print(uw_serializer.errors)
                return JsonResponse(uw_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as err:
        error_dict = {"error": str(err)}
        return JsonResponse(error_dict, safe=False)


# class UserRegistration(APIView):
#     def post(self, request, format=None):
#         try:            
#             to_email = []
#             serializer = UserSerializer(data=request.data)
#             data = {}
#             if serializer.is_valid():
#                 user = serializer.save()
#                 data['response'] = "Successfully registered a new usere"
#                 data['email'] = user.email
#                 mail_subject = 'User Registrations Email Confirmation '
#                 to = str(user.email)
#                 to_email.append(to)
#                 message =  "Hi, welcome to the CarrerPedia Platform."
#                 send_mail(mail_subject, message, HOST_EMAIL, to_email, fail_silently=False,)
#             else:
#                 data = serializer.errors
#             return Response(data)
#         except Exception as err:
#             error_dict = {"error": str(err)}
#             return JsonResponse(error_dict, safe=False)


# @permission_classes((IsAuthenticated,))
# @api_view(['POST'])
# def update_user_details(request):
#     """ For updating user Details.."""
#     try:
#         req_data = request.data
#         if request.method == 'POST':
#             if "email" in req_data:
#                 user_objs = User.objects.filter(email=req_data['email'])
#                 if user_objs:
#                     user = user_objs[0]
#                     serializer = UserSerializer(user, data=req_data)
#                 else:
#                     serializer = UserSerializer(data=req_data)                        
#             if serializer.is_valid():
#                 serializer.save()
#                 return JsonResponse(serializer.data, status=status.HTTP_202_ACCEPTED)
#             else:
#                 print(serializer.errors)
#                 return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         else:
#             return HttpResponse(status=status.HTTP_404_NOT_FOUND)
#     except Exception as err:
#         error_dict = {"error": str(err)}
#         return JsonResponse(error_dict, safe=False)



