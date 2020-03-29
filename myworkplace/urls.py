from django.urls import path, include
from rest_framework import routers

from . import views
# app_name = 'myworkplace'

router = routers.DefaultRouter()
router.register(r'questions', views.QuestionViewSet)
router1 = routers.DefaultRouter()
router1.register(r'emailemployees', views.EmailViewSet)
router2 = routers.DefaultRouter()
router2.register(r'employee', views.EmployeeViewSet)


urlpatterns = [
    path('', views.home, name='home'),
    path('daily_update/<id>/', views.daily_update, name='daily_update'),
    path('normal1/<id>/', views.normal1, name='normal1'),
    path('normal2/<id>/', views.normal2, name='normal2'),
    path('quarantine/<id>/<existing_health>/', views.quarantine, name='quarantine'),
    path('checkin/<id>/', views.checkin, name='checkin'),
    path('tscheckin/<time>/', views.tscheckin, name='tscheckin'),
    path('tscheckout/<time>/', views.tscheckout, name='tscheckin'),
    path('personal_info/<id>/', views.personal_info, name='personal_info'),
    path('api/', include(router.urls)),
    path('api1', include(router1.urls)),
    path('api2', include(router2.urls)),
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
    path('summarylist/', views.summarylist, name='summarylist'),
    path('summarylist1/<dept_sap>/', views.summarylist1, name='summarylist1'),
    path('remove_duplicate_all/', views.remove_duplicate_all, name='remove_duplicate_all'),
    path('remove_duplicate_emp_id/<emp_id>/', views.remove_duplicate_emp_id, name='remove_duplicate_emp_id'),
    path('remove_line_emp_id/<emp_line_id>/', views.remove_line_emp_id, name='remove_line_emp_id'),
    path('update_employee_profile/', views.update_employee_profile, name='update_employee_profile'),
    path('update_employee_profile2/', views.update_employee_profile2, name='update_employee_profile2'),
    path('update_employee_profile3/', views.update_employee_profile3, name='update_employee_profile3'),

    path('upload_director_email1/', views.upload_director_email1, name='upload_director_email1'),
    path('upload_director_email2/', views.upload_director_email2, name='upload_director_email2'),
    path('upload_director_email3/', views.upload_director_email3, name='upload_director_email3'),
    path('upload_director_email4/', views.upload_director_email4, name='upload_director_email4'),

    # path('update_directror_email/<id>/', views.update_directror_email, name='update_directror_email'),

]
