from django.urls import path, include

from . import views

urlpatterns = [
    path('send_email_leave_covid/<id>/<boss>/', views.send_email_leave_covid, name='send_email_leave_covid'),
    path('send_email_leave_wfh_2/<id>/<boss>/', views.send_email_leave_wfh_2, name='send_email_leave_wfh_2'),
    path('send_email_leave_wfh_1/<id>/<boss>/<day>/', views.send_email_leave_wfh_1, name='send_email_leave_wfh_1'),
    path('confirm_leave_WFH_2/<id>/<boss>/', views.confirm_leave_WFH_2, name='confirm_leave_WFH2'),
    path('confirm_leave_WFH_1/<id>/<boss>/<day>', views.confirm_leave_WFH_1, name='confirm_leave_WFH1'),
        ]