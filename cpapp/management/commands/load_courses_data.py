# loading csv file data

import pandas as pd
import os
from django.db.models import Q
from django.core.management.base import BaseCommand
from django.utils import timezone
from cpapp.models import Course, Opportunity, Subject
from cpapp.serializers import (CourseSerializer, OpportunitySerializer, SubjectSerializer,)


TOP_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CSV_FILES = ['course_descriptions', 'career_opportunities', 'course_subjects']


def load_course_details(data_df):
    print("Started loading courses details")
    d_records = data_df.to_dict('records')
    for item in d_records:
        if str(item["field"]) == "nan":
            item["field"] = ""
        cour_obj = Course.objects.filter(Q(course=item["course"]) & Q(uid=item["uid"]))
        if not cour_obj:
            print("Saving Course: {} {}".format(item["course"], item["uid"]))
            cour_serializer = CourseSerializer(data=item)               
            if cour_serializer.is_valid():
                cour_serializer.save()                
            else:
                print(cour_serializer.errors)
        else:
            print("Course exists already so skipping ..")            
    print("End loading courses details")


def load_opportunities(data_df):
    print("Started loading course opportunities")
    d_records = data_df.to_dict('records')
    for item in d_records:
        new_item = {"name":item["opportunities"], "course":item["uid"]}
        opp_objs = Opportunity.objects.filter(Q(course__uid=new_item["course"]) & Q(name=new_item["name"]))
        if not opp_objs:
            print("Saving Opportunity: {} {}".format(new_item["course"], new_item["name"]))
            op_serializer = OpportunitySerializer(data=new_item)
            if op_serializer.is_valid():
                op_serializer.save()                
            else:
                print(op_serializer.errors)
        else:
            print("Opportunity exists already so skipping ..") 
        print("End loading course opportunities")


def load_subjects(data_df):
    print("Started loading course subjects")
    d_records = data_df.to_dict('records')
    for item in d_records:
        new_item = {"name":item["subjects"], "course":item["uid"]}
        sub_objs = Subject.objects.filter(Q(course__uid=new_item["course"]) & Q(name=new_item["name"]))
        if not sub_objs:
            print("Saving Subject: {} {}".format(new_item["course"], new_item["name"]))
            sub_serializer = SubjectSerializer(data=new_item)
            if sub_serializer.is_valid():
                sub_serializer.save()                
            else:
                print(sub_serializer.errors)
        else:
            print("Subject exists already so skipping ..")  
    print("End loading course subjects")


class Command(BaseCommand):
    help = 'Loads all Course releated data into DB'
    
    def handle(self, *args, **kwargs):
        try:
            for file_name in CSV_FILES:
                full_f_path = os.path.join(TOP_DIR, "csv_data", file_name+".csv")
                if os.path.exists(full_f_path):
                    data_f = pd.read_csv(full_f_path, encoding="utf-8")
                    if "description" in file_name:
                        load_course_details(data_f)
                    elif "opportunities" in file_name:
                        load_opportunities(data_f)
                    elif "subjects" in file_name:
                        load_subjects(data_f)
        except Exception as err:
            print("Error occurred while loading data: {}".str(err))
        