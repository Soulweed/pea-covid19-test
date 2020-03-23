from django.urls import path, include
from rest_framework import routers

from . import views
# app_name = 'myworkplace'

router = routers.DefaultRouter()
router.register(r'questions', views.QuestionViewSet)
router1 = routers.DefaultRouter()
router1.register(r'emailemployees', views.EmailViewSet)

urlpatterns = [
    path('', views.home, name='home'),
    path('daily_update/<id>/', views.daily_update, name='daily_update'),
    path('screen/<id>/', views.screen, name='screen'),
    path('confirm/<id>', views.confirm, name='confirm'),
    path('normal_group/<id>/', views.normal_group, name='normal_group'),
    path('medium_group/<id>/', views.medium_group, name='medium_group'),
    path('risk_group/<id>/', views.risk_group, name='risk_group'),
    path('risk_form/<id>/', views.risk_form, name='risk_form'),
    path('checkin/<id>/', views.checkin, name='checkin'),
    path('tscheckin/<id>/', views.tscheckin, name='tscheckin'),
    path('tscheckout/<id>/', views.tscheckout, name='tscheckin'),
    path('confirm_WFH/<id>/', views.confirm_WFH, name='confirm_WFH'),
    path('personal_info/<id>/', views.personal_info, name='personal_info'),
    path('api/', include(router.urls)),
    path('api1', include(router1.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('confirm_registration/<id>/', views.confirm_registration, name='confirm_registration'),
    path('challenge2/<id>/', views.randomquestions, name='challenge'),
    path('correct/', views.correct, name='correct'),
    path('wrong/', views.wrong, name='wrong'),
    path('miss3d_du/<id>/', views.miss3d_du, name='miss3d_du'),
    path('miss3d_ts/<id>/', views.miss3d_ts, name='miss3d_ts'),
    path('register/<id>/', views.register, name='register'),
    path('WFH_request/<id>/<boss>/', views.WFH_request, name='WFH_request'),
    path('LEAVE_request/<id>/<boss>/', views.LEAVE_request, name='LEAVE_request'),
    path('WFH_approve/<id>/<boss>/', views.WFH_approve, name='WFH_approve'),
    # path('LEAVE_approve/<id>/<boss>/', views.LEAVE_approve, name='LEAVE_approve'),


]
