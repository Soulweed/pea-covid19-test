from rest_framework import serializers
from .models import question ,emailemployee ,employee

class QuestionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = question
        fields = ('question_text', 'answer_1' , 'answer_2' , 'answer_3' , 'correct_answer')

class EmailSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = emailemployee
        fields = ('employeeid', 'employeeemail' )

class EmployeeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = employee
        fields = ('employee_ID', 'emplyee_name' ,'activity_text','activity_daily_update','activity_challenge','activity_checkin','activity_checkout')


