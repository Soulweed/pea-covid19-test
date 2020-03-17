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
    path('confirm/<id>/', views.confirm, name='confirm'),
    path('normal_group/<id>/', views.normal_group, name='normal_group'),
    path('medium_group/<id>/', views.medium_group, name='medium_group'),
    path('risk_group/<id>/', views.risk_group, name='risk_group'),

    path('checkin/<id>/', views.checkin, name='checkin'),
    path('confirm_WFH/<id>/', views.confirm, name='confirm_WFH'),
    path('personal_info/<id>/', views.personal_info, name='personal_info'),
    path('callback/', views.callback, name='callback'),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),


]
