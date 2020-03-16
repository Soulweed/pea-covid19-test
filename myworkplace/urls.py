from django.urls import path, include
from rest_framework import routers

from . import views
# app_name = 'myworkplace'

router = routers.DefaultRouter()
router.register(r'questions', views.QuestionViewSet)

urlpatterns = [
    path('', views.home, name='home'),
    path('daily_update<int=id>/', views.daily_update, name='daily_update'),
    path('callback/', views.callback, name='callback'),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

]
