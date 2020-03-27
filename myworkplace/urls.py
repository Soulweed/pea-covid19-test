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
    path('normal1/<id>/', views.normal1, name='normal1'),
    path('normal2/<id>/', views.normal2, name='normal2'),
    path('quarantine/<id>/<existing_health>/', views.quarantine, name='quarantine'),
    # path('see_doctor/', views.see_doctor, name='see_doctor'),
    path('checkin/<id>/', views.checkin, name='checkin'),
    path('tscheckin/<time>/', views.tscheckin, name='tscheckin'),
    path('tscheckout/<time>/', views.tscheckout, name='tscheckin'),
    path('personal_info/<id>/', views.personal_info, name='personal_info'),
    path('api/', include(router.urls)),
    path('api1', include(router1.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('challenge2/<id>/', views.randomquestions, name='challenge'),
    path('correct/', views.correct, name='correct'),
    path('wrong/', views.wrong, name='wrong'),
    path('miss3d_du/<id>/', views.miss3d_du, name='miss3d_du'),
    path('miss3d_ts/<id>/', views.miss3d_ts, name='miss3d_ts'),
    path('register/<id>/', views.register, name='register'),
    # path('WFH_request/<id>/<boss>/', views.WFH_request, name='WFH_request'),
    path('LEAVE_request/<id>/', views.LEAVE_request, name='LEAVE_request'),
    path('WFH_approve/<id>/<boss>/<total_date>/', views.WFH_approve, name='WFH_approve'),
    path('meet_doc2/<id>/', views.meet_doc2, name='meet_doc2'),
    path('formwfh1/<id>/', views.formwfh1, name='formwfh1'),
    path('formwfh2/<id>/', views.formwfh2, name='formwfh2'),
    path('resultscreen2/', views.resultscreen2, name='resultscreen2'),
    path('resultscreen3/', views.resultscreen3, name='resultscreen3'),
    path('formleave/<id>', views.LEAVE_request, name='formleave'),
    path('test/', views.test, name='test'),
    path('removeid/', views.removeid, name='removeid'),
    path('summarylist/', views.summarylist, name='summarylist'),
    path('remove_one_emp_id/<emp_id>/', views.remove_one_emp_id, name='remove_one_emp_id'),
    path('remove_duplicate_emp_id/<emp_id>', views.remove_duplicate_emp_id, name='remove_duplicate_emp_id'),
]
