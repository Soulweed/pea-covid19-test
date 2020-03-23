from rest_framework import serializers
from .models import question ,emailemployee

class QuestionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = question
        fields = ('question_text', 'answer_1' , 'answer_2' , 'answer_3' , 'correct_answer')

class EmailSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = emailemployee
        fields = ('employeeid', 'employeeemail' )