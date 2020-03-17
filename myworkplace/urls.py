from django.urls import path, include
from rest_framework import routers

from . import views
# app_name = 'myworkplace'

router = routers.DefaultRouter()
router.register(r'questions', views.QuestionViewSet)

urlpatterns = [
    path('', views.home, name='home'),
    path('daily_update/<id>/', views.daily_update, name='daily_update'),
    path('screen/<id>/', views.screen, name='screen'),
    path('confirm_screen/<id>/', views.confirm_screen, name='confirm_screen'),
    path('personal_info/<id>/', views.personal_info, name='personal_info'),
    path('callback/', views.callback, name='callback'),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
