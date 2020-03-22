from django.urls import path, include
from .views import callback, send_question

urlpatterns = [
    path('callback/', callback, name='callback'),
    path('send_question/', send_question, name='question'),
]

