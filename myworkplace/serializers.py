from rest_framework import serializers
from .models import question

class QuestionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = question
        fields = ('question_text', 'answer_1' , 'answer_2' , 'answer_3' , 'correct_answer')