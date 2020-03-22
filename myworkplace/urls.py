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
    path('risk_form/<id>/', views.risk_form, name='risk_form'),
    path('checkin/<id>/', views.checkin, name='checkin'),
    # path('challenge/<id>/', views.challenge, name='challenge'),
    # path('send_question/', views.send_question, name='question'),
    path('confirm_WFH/<id>/', views.confirm, name='confirm_WFH'),
    path('personal_info/<id>/', views.personal_info, name='personal_info'),
    # path('callback/', views.callback, name='callback'),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('confirm_registration/<id>/', views.confirm_registration, name='confirm_registration'),
    path('challenge2/<id>/', views.randomquestions, name='challenge'),
    path('correct/', views.correct, name='correct'),
    path('wrong/', views.wrong, name='wrong'),
    path('send_email_leave_covid/<id>/<boss>/', views.send_email_leave_covid, name='send_email_leave_covid'),
    path('send_email_leave_wfh_2/<id>/<boss>/', views.send_email_leave_wfh_2, name='send_email_leave_wfh_2'),
    path('send_email_leave_wfh_1/<id>/<boss>/<day>/', views.send_email_leave_wfh_1, name='send_email_leave_wfh_1'),
    path('confirm_leave_WFH_2/<id>/<boss>/', views.confirm_leave_WFH_2, name='confirm_leave_WFH2'),
    path('confirm_leave_WFH_1/<id>/<boss>/<day>', views.confirm_leave_WFH_1, name='confirm_leave_WFH1'),
    path('miss3d_du/<id>/', views.miss3d_du, name='miss3d_du'),
    path('miss3d_ts/<id>/', views.miss3d_ts, name='miss3d_ts'),
    path('register/<id>/', views.register, name='register'),
]
