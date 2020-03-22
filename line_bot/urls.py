from django.urls import path, include
from .views import callback


path('callback/', callback, name='callback'),
