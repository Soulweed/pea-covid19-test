from django.shortcuts import render, redirect
from django.core.exceptions import MultipleObjectsReturned
from django.db import connection
from .models import employee, question, emailemployee
from send_email.views import send_email_wfh_request,get_user_email, send_email_wfh14day_request, send_email_confrim_register, \
    send_email_meetdoc_request, send_email_confrim_wfh
import json
from datetime import datetime, timedelta, date
import getpass
from collections import defaultdict
from exchangelib import Configuration, Account, DELEGATE, Credentials
from exchangelib import Message, Mailbox, FileAttachment
import base64
import requests, xmltodict
import random

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned


# importing email library
from django.core.mail import send_mail
from django.conf import settings
from django import forms


class CheckinForm(forms.Form):
    content = forms.CharField(max_length=150)

class CheckoutForm(forms.Form):
    content = forms.CharField(max_length=150)


# Create your views here.
def home(request):
    context = {'number_of_employee': employee.objects.count(),
               'high_risk':employee.objects.filter(active_status='COVID').count(),
               'normal_wfh':employee.objects.filter(active_status='WFH').count(),
               'risk_wfh':employee.objects.filter(active_status='Leave').count(),
               'pea_office':employee.objects.filter(active_status='PEA').count(),
               'no_daily_update':employee.objects.filter(daily_update=False).count(),
               'update_date':datetime.now().strftime("%Y-%m-%d")}
    print(context)
    return render(request, 'myworkplace/home.html', context)

def daily_update(request, id):
    if request.method == "POST":
        dangerous_area = request.POST.get("question1")
        working_with_foreigner = request.POST.get("question2")
        contact_with_infected = request.POST.get("question3")
        doctor = request.POST.get("question4")
        stay_in_infected_place = request.POST.get("question5")
        fever = request.POST.get("fever")
        cough = request.POST.get("cough")
        cold = request.POST.get("runnynose")
        sore_throat = request.POST.get("throatache")
        tried = request.POST.get("tired")
        list_group_1 = [dangerous_area, working_with_foreigner, contact_with_infected, doctor, stay_in_infected_place]
        list_group_2 = [fever, cough, cold, sore_throat, tried]
        group1 = list_group_1.count('TRUE')
        group2 = list_group_2.count('on')
        if group1 == 0 and group2 == 0:
            health = 'normal'
        elif (group1 > 0 and group2 == 0) or (group1 > 0 and group2 == 1):
            health = 'quarantine'
        elif (group1 == 0 and group2 > 0 ):
            health = 'flu'
        elif (group1 == 1 and group2 > 1) or (group1 > 1 and group2 > 1):
            health = 'hospital'
        obj = {'type': 'daily_update', 'health': health, 'datetime': datetime.now().strftime("%Y-%m-%d (%H:%M:%S)")}
        try:
            user_DU = employee.objects.get(employee_ID=id)
            data = json.loads(user_DU.activity_daily_update)
            data.append(obj)
            user_DU.activity_daily_update = json.dumps(data)
            existing_health=user_DU.healthy
            user_DU.healthy=health
            user_DU.daily_update=True
            user_DU.save()
            connection.close()
            if health == 'normal':

                return redirect(normal1, id)
            elif health == 'flu':

                return redirect(normal2, id)
            elif health =='quarantine':

                return redirect(quarantine, id, existing_health)
            elif health =='hospital':

                return redirect(meet_doc2, id)
        except MultipleObjectsReturned:
            print('ERROR DU dubplicate id: {}'.format(id))
            remove_emp_id(id)
            print('DU dubplicate id: {} is removed'.format(id))
    return render(request, 'myworkplace/daily_update.html')

def LEAVE_request(request, id):
    context ={'EmployeeID': id,}
    email=''
    if request.method == "POST":
        page = request.POST.get("page")
        if (page == "1"):
            # print(page)
            # print("OK1")
            return render(request, 'myworkplace/formleave2.html', context)
        if (page == "2"):
            id_boss = request.POST.get("id_boss")
            total_day = 14
            startdate=(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            enddate=(datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d")
            first_name, last_name, sex_desc, posi_text_short, dept_sap_short, dept_sap, dept_upper, sub_region, emp_email = get_user_email(id_boss)
            # FirstName, LastName, DepartmentShort, PositionDescShort, LevelDesc , Gender= get_employee_profile(
            #     id_boss)
            context={'id_boss': id_boss, 'email_boss': email, 'total_day': total_day,'startdate':startdate, 'enddate':enddate,
                            'boss_name': '{} {}'.format(first_name, last_name), 'JobDesc': posi_text_short, 'Gender':sex_desc}
            return render(request, 'myworkplace/formleave3.html', context)
        if (page == "3"):
            # email = request.POST.get("email_boss")  #เอา email จาก ที่ซ่อนใว้ใน hidden ใน formleave3
            boss_email = request.POST.get("email_boss")  #เอา email จาก ที่ซ่อนใว้ใน hidden ใน formleave3
            id_boss=request.POST.get("id_boss")
            startdate=(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            enddate=(datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d")
            obj = {'type': 'wfh14days_request', 'startdate': startdate, 'enddate':enddate,
                   'datetime': datetime.now().strftime("%Y-%m-%d (%H:%M:%S)"), 'sent_request_to':{'id':id_boss, 'email':boss_email}}
            try:
                user_LEAVE_request = employee.objects.get(employee_ID=str(id))
                data = json.loads(user_LEAVE_request.activity_text)
                data.append(obj)
                user_LEAVE_request.activity_text = json.dumps(data, ensure_ascii=False)
                user_LEAVE_request.approved_status = 'Leave'
                user_LEAVE_request.employee_id_up_1=id_boss
                user_LEAVE_request.employee_id_up_2=boss_email
                user_LEAVE_request.save()
                connection.close()
                send_email_wfh14day_request(id=id, email_boss=email, name=user_LEAVE_request.emplyee_name, startdate=startdate, enddate=enddate)
                return render(request, 'myworkplace/formleave4.html', context)
            except MultipleObjectsReturned:
                print('ERROR LEAVE request : {}'.format(id))
                remove_emp_id(id)
                print('Remove duplicate LEAVE request : {}'.format(id))

    return render(request, 'myworkplace/formleave1.html', context)

def formwfh1(request, id):
    if request.method == "POST":
        return redirect(formwfh2, id)
    return render(request, 'myworkplace/formwfh1.html')

def formwfh2(request,id):
    context = {'id':id}
    if request.method == "POST":
        page = request.POST.get("page")
        if (page == "1"):
            # print(page)
            id_boss = request.POST.get("director")
            get_startdate = request.POST.get("startdate")
            get_enddate = request.POST.get("enddate")
            startdate = datetime.strptime(get_startdate, "%Y-%m-%d").date()
            enddate = datetime.strptime(get_enddate, "%Y-%m-%d").date()
            delta = enddate - startdate
            total_date = delta.days + 1
            first_name, last_name, sex_desc, posi_text_short, dept_sap_short, dept_sap, dept_upper, sub_region,emp_email = get_user_email(id_boss)

            # FirstName, LastName, DepartmentShort, PositionDescShort, LevelDesc, Gender = get_employee_profile(
            #     id_boss)
            context={'Boss_name':'{} {}'.format(first_name, last_name), 'Boss_position':posi_text_short, 'Gender':sex_desc,
                     'startdate':get_startdate, 'enddate':get_enddate, 'total_date':total_date, 'email_boss':emp_email, 'id_boss':id_boss}
            # print(context)
            return render(request, 'myworkplace/formwfh3.html', context)
        if (page=="2"):
            boss_email = request.POST.get("email_boss")  #เอา email จาก ที่ซ่อนใว้ใน hidden ใน formleave3
            id_boss=request.POST.get("id_boss")
            get_total_date =request.POST.get("total_date")
            get_startdate =request.POST.get("startdate")
            get_enddate =request.POST.get("enddate")
            obj = {'type': 'wfh_request', 'startdate': get_startdate, 'enddate':get_enddate,
                   'datetime': datetime.now().strftime("%Y-%m-%d (%H:%M:%S)"), 'sent_request_to':{'id':id_boss, 'email':boss_email}}
            try:
                user_formwfh2 = employee.objects.get(employee_ID=str(id))
                data = json.loads(user_formwfh2.activity_text)
                data.append(obj)
                user_formwfh2.activity_text = json.dumps(data, ensure_ascii=False)
                user_formwfh2.approved_status = 'WFH'
                user_formwfh2.WFH_start_date=get_startdate
                user_formwfh2.WFH_end_date=get_enddate
                user_formwfh2.employee_id_up_1=id_boss
                user_formwfh2.employee_id_up_2=boss_email
                user_formwfh2.save()
                connection.close()
                send_email_wfh_request(id=id, email_boss=boss_email, total_date=get_total_date, name=user_formwfh2.emplyee_name, startdate=get_startdate, enddate=get_enddate)
                return render(request, 'myworkplace/formwfh4.html')
            except MultipleObjectsReturned:
                print('ERROR wfh request id: {}'.format(id))
                remove_emp_id(id)
                print('Remove duplicate wfh request : {}'.format(id))
    return render(request, 'myworkplace/formwfh2drange.html', context)

def meet_doc2(request,id):
    context = {'id':id}
    if request.method == 'POST':
        page = request.POST.get('page')
        if(page == "1"):
            # id_boss = request.POST.get("director")
            boss_email = request.POST.get("email_boss")  #เอา email จาก ที่ซ่อนใว้ใน hidden ใน formleave3
            id_boss=request.POST.get("id_boss")

            first_name, last_name, sex_desc, posi_text_short, dept_sap_short,dept_sap, dept_upper, sub_region, email = get_user_email(id_boss)
            startdate=(datetime.now() + timedelta(days=1)).strftime("%Y/%m/%d")

            enddate=(datetime.now() + timedelta(days=15)).strftime("%Y/%m/%d")
            obj = {'type': 'meet_doc_request', 'startdate': startdate, 'enddate':enddate,
                   'datetime': datetime.now().strftime("%Y/%m/%d (%H:%M:%S)"), 'sent_request_to':{'id':id_boss, 'email':boss_email}}
            try:
                user_meet_doc2 = employee.objects.get(employee_ID=str(id))
                data = json.loads(user_meet_doc2.activity_text)
                data.append(obj)
                user_meet_doc2.activity_text = json.dumps(data, ensure_ascii=False)
                user_meet_doc2.active_status = 'LEAVE'
                user_meet_doc2.approved_status = 'Idle'
                user_meet_doc2.LEAVE_start_date=startdate
                user_meet_doc2.LEAVE_end_date=enddate
                user_meet_doc2.employee_id_up_1=id_boss
                user_meet_doc2.employee_id_up_2=boss_email
                user_meet_doc2.save()
                connection.close()
                send_email_meetdoc_request(id=id, email_boss=email, name=user_meet_doc2.emplyee_name)
                return render(request, 'myworkplace/formseedoc3.html', context)
            except MultipleObjectsReturned:
                print('ERROR meet doc request id: {}'.format(id))
                remove_emp_id(id)
                print('Remove duplicate meet doc request : {}'.format(id))
    return render(request, 'myworkplace/formseedoc2.html', context)

def personal_info(request, id):
    try:
        data_personal_info = employee.objects.get(employee_line_ID=id)
        context = {'data': data_personal_info.__dict__}
        connection.close()
        return render(request, 'myworkplace/personal_info.html', context)
    except MultipleObjectsReturned:
        print('ERROR personal info  id: {}'.format(id))
        remove_emp_id(id)
        print('Remove personal info  wfh request : {}'.format(id))

def checkin(request, id):
    if request.method == "POST":
        action_type = request.POST.get("type")
        checkin_status=request.POST.get("checkinStatus")
        checkout_status = request.POST.get("checkoutStatus")
        if (checkin_status == 'not' and action_type == 'checkin') or (checkout_status == 'not' and action_type == 'checkout'):
            return render(request, 'myworkplace/timestamp_lock.html')
        else:
            latitude = request.POST.get("latitude")
            longitude = request.POST.get("longitude")
            if(action_type == "checkin"):
                obj = {'type': action_type, 'latitude': latitude, 'longitude': longitude,
                       'datetime': datetime.now().strftime("%Y-%m-%d (%H:%M:%S)")}
                try:
                    user_checkin = employee.objects.get(employee_ID=str(id))
                    data = json.loads(user_checkin.activity_checkin)
                    data.append(obj)
                    user_checkin.activity_checkin = json.dumps(data, ensure_ascii=False)
                    user_checkin.save()
                    connection.close()
                    return redirect(tscheckin, obj['datetime'])
                except MultipleObjectsReturned:
                    print('ERROR Checkin duplicate id: {}'.format(id))
                    remove_emp_id(id)
                    print('Remove Checkin duplicate id: {}'.format(id))
            elif(action_type == "checkout"):
                obj = {'type': action_type, 'latitude': latitude, 'longitude': longitude,
                       'datetime': datetime.now().strftime("%Y-%m-%d (%H:%M:%S)")}
                try:
                    user_checkout = employee.objects.get(employee_ID=str(id))
                    data = json.loads(user_checkout.activity_checkout)
                    data.append(obj)
                    user_checkout.activity_checkout = json.dumps(data, ensure_ascii=False)
                    user_checkout.save()
                    connection.close()
                    return redirect(tscheckout, obj['datetime'])
                except MultipleObjectsReturned:
                    print('ERROR Checkin duplicate id: {}'.format(id))
                    remove_emp_id(id)
                    print('Remove Checkin duplicate id: {}'.format(id))
    return render(request, 'myworkplace/timestamp.html')

def tscheckin(request, time):
    d=time.split()[0]
    t=time.split()[-1][1:-1]
    context={'date':d, 'time':t}
    return render(request, 'myworkplace/tscheckin.html', context)

def tscheckout(request, time):
    d=time.split()[0]
    t=time.split()[-1][1:-1]
    context={'date':d, 'time':t}
    return render(request, 'myworkplace/tscheckout.html', context)

def normal1(request, id):
    if request.method == "POST":
        return redirect(formwfh1, id)
    return render(request, 'myworkplace/normal1.html')

def normal2(request, id):
    if request.method == "POST":
        return redirect(formwfh1, id)
    return render(request, 'myworkplace/normal2.html')

def resultscreen2(request):
    return render(request, 'myworkplace/resultscreen2.html')

def resultscreen3(request):
    return render(request, 'myworkplace/resultscreen3.html')

def quarantine(request,id, existing_health):
    context={'data':existing_health}
    if request.method == "POST":
        return redirect(LEAVE_request, id)
    return render(request, 'myworkplace/quarantine.html', context)

# API
from rest_framework import viewsets
from .serializers import QuestionSerializer, EmailSerializer

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = question.objects.all().order_by('question_text')
    serializer_class = QuestionSerializer

class EmailViewSet(viewsets.ModelViewSet):
    queryset = emailemployee.objects.all().order_by('employeeid')
    serializer_class = EmailSerializer


from django.http import HttpResponseForbidden, HttpResponse
from django.views.decorators.csrf import csrf_exempt

def register(request,id):
    emp_id = id[33:]
    line_id = id[0:33]

    # employee_line_id_list=employee.objects.filter(employee_line_ID=line_id).values_list(flat=True).distinct()
    # connection.close()
    # if line_id in employee_line_id_list:
    #     return redirect(home)
    # else:
    # try:
    #     n = Oficio.objects.get(numero=number)
    #     # number already exists
    #     return False
    # except ObjectDoesNotExist:
    #     # number does not exist
    #     oficio = Oficio(numero=number)
    #     oficio.save()
    #     return True
    try:
        user=employee.objects.get(employee_line_ID=line_id)
        connection.close()
        return redirect(home)
    except MultipleObjectsReturned:
        print('ERROR register duplicate id: {}'.format(id))
        remove_emp_id(id)
        print('Remove register duplicate id: {}'.format(id))
    except ObjectDoesNotExist:
        first_name, last_name, sex_desc, posi_text_short, dept_sap_short, dept_sap, dept_upper, sub_region, emp_email = get_user_email(emp_id)

    # FirstName, LastName, DepartmentShort, PositionDescShort, LevelDesc, Gender= get_employee_profile(emp_id)

        context ={'EmployeeID': emp_id, 'FirstName':first_name, 'LastName':last_name, 'DepartmentShort':dept_sap_short,
                  'PositionDescShort':posi_text_short,  'Gender':sex_desc}
        sex = ''
        age = ''
        tel = ''
        work_place = ''
        work_building = ''
        work_floor = ''

        address_no = ''
        address_tumbol = ''
        address_amphur = ''
        address_province = ''
        address_type = ''
        address_to_live = ''
        detention_place = ''

        blood = ''
        congenital_disease_status = ''
        congenital_disease = ''
        drug_allergy_history_status = ''
        drug_allergy_history = ''
        respiratory_disease_status = ''
        respiratory_disease = ''
        last_disease = ''
        last_hospital = ''
        last_time_status = ''
        favorite_hospital = ''

        close_person_first_name = ''
        close_person_last_name = ''
        close_person_tel = ''
        close_person_relationship = ''
        workmate_first_name = ''
        workmate_last_name = ''
        workmate_tel = ''
        emergency_one_first_name = ''
        emergency_one_last_name = ''
        emergency_one_tel = ''
        emergency_two_first_name = ''
        emergency_two_last_name = ''
        emergency_two_tel = ''

        if request.method == "POST":
            # emp_name = request.POST.get("first-last name")
            ext = request.POST.get("ext")  # หมายเลขโทรศัพท์ภายใน
            mobile_phone = request.POST.get("mobile_phone")  # หมายเลขโทรศัพท์มือถือ
            building = request.POST.get("building")  # อาคาร
            floor = request.POST.get("floor")  # ชั้น
            address = request.POST.get("address")
            # selector = request.POST.get("selector")
            addition_address = request.POST.get("addition_address")
            firstname_ref_1 = request.POST.get("firstname_ref_1")
            lastname_ref_1 = request.POST.get("lastname_ref_1")
            mobile_ref_1 = request.POST.get("mobile_ref_1")
            relation_ref_1 = request.POST.get("relation_ref_1")


            first_name, last_name, sex_desc, posi_text_short, dept_sap_short, dept_sap, dept_upper, sub_region, emp_email = get_user_email(emp_id)
            obj = {'type': 'register', 'datetime': datetime.now().strftime("%Y-%m-%d (%H:%M:%S)")}
            user_data = employee(
                emplyee_name='{} {}'.format(first_name, last_name),
                employee_ID=emp_id,
                employee_line_ID=line_id,
                activity_text=json.dumps([obj], ensure_ascii=False),
                # posi_text_short=posi_text_short,
                employee_posi_text_short=posi_text_short,
                employee_dept_sap_short = dept_sap_short,
                employee_dept_sap = dept_sap,
                employee_dept_upper = dept_upper,
                employee_sub_region = sub_region,
                employee_emp_email = emp_email,
                employee_tel=ext,
                tel=mobile_phone,
                work_building = building,
                work_floor = floor,
                address_type=address,
                address_to_live=addition_address,
                workmate_first_name=firstname_ref_1,
                workmate_last_name=lastname_ref_1,
                workmate_tel=mobile_ref_1,
                workmate_id=relation_ref_1,
            )
            user_data.save()
            print('------------------------')
            print('model save: {}'.format(emp_id))
            print('------------------------')
            connection.close()
            send_email_confrim_register(emp_id=emp_id, emp_email=emp_email)
            return redirect(daily_update,emp_id)
        return render(request, 'myworkplace/formregister.html', context)

######## challenge

def randomquestions(request, id):
    ranquestions = question.objects.get(pk=random.randint(0, len(question.objects.all()) - 1))
    context = {'data': ranquestions}
    if request.method == "POST":
        answer = request.POST.get("exampleRadios")
        correct = request.POST.get("correct")
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")
        obj = {'type': 'question', 'answer':answer==correct, 'latitude': latitude, 'longitude': longitude,
               'datetime': datetime.now().strftime("%Y-%m-%d (%H:%M:%S)")}
        try:
            user_question = employee.objects.get(employee_ID=str(id))
            data = json.loads(user_question.activity_challenge)
            data.append(obj)
            user_question.activity_text = json.dumps(data, ensure_ascii=False)
            user_question.save()
            connection.close()
            if (answer == correct):
                return render(request, 'myworkplace/correct.html')
            else:
                return render(request, 'myworkplace/wrong.html')
        except MultipleObjectsReturned:
            print('ERROR randomquestions duplicate id: {}'.format(id))
            remove_emp_id(id)
            print('Remove randomquestions duplicate id: {}'.format(id))
    return render(request, 'myworkplace/challenge2.html', context)

def wrong(request):
    return render(request, 'myworkplace/wrong.html')

def correct(request):
    return render(request, 'myworkplace/correct.html')

def miss3d_du(request, id):
    try:
        data_miss3d_du = employee.objects.get(employee_ID=str(id))
        context = {'data': data_miss3d_du.__dict__}
        connection.close()
        return render(request, 'myworkplace/miss3d_du_id.html', context)
    except MultipleObjectsReturned:
        print('ERROR miss3d_du duplicate id: {}'.format(id))
        remove_emp_id(id)
        print('Remove miss3d_du duplicate id: {}'.format(id))


def miss3d_ts(request, id):
    try:
        data_miss3d_ts = employee.objects.get(employee_ID=str(id))
        context = {'data': data_miss3d_ts.__dict__, 'number':40}
        connection.close()
        return render(request, 'myworkplace/miss3d_ts_id.html', context)
    except MultipleObjectsReturned:
        print('ERROR miss3d_ts duplicate id: {}'.format(id))
        remove_emp_id(id)
        print('Remove miss3d_ts duplicate id: {}'.format(id))

def WFH_approve(request, id, boss, total_date):

    obj = {'type': 'WFH_approved', 'approved_by': boss,
           'start_date': (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
           'finish_date': (datetime.now() + timedelta(days=int(total_date))).strftime("%Y-%m-%d"),
           'datetime': datetime.now().strftime("%Y-%m-%d (%H:%M:%S)")}
    try:
        user_WFH_approve = employee.objects.get(employee_ID=str(id))
        data = json.loads(user_WFH_approve.activity_text)
        data.append(obj)
        user_WFH_approve.activity_text = json.dumps(data, ensure_ascii=False)
        user_WFH_approve.active_status='WFH'
        user_WFH_approve.approved_status='Idle'
        user_WFH_approve.save()
        connection.close()
        first_name, last_name, sex_desc, posi_text_short, dept_sap_short, dept_sap, dept_upper, sub_region, emp_email = get_user_email(id)
        send_email_confrim_wfh(boss=boss, emp_email=emp_email)
        return render(request, 'myworkplace/test2.html')
    except MultipleObjectsReturned:
        ('ERROR WFH_approve duplicate id: {}'.format(id))
        remove_emp_id(id)
        print('Remove WFH_approve duplicate id: {}'.format(id))

def LEAVE_approve(request, id, boss):
    day=14
    obj = {'type': 'LEAVE_request', 'approved_by': boss,
           'start_date': (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
           'finish_date': (datetime.now() + timedelta(days=int(day))).strftime("%Y-%m-%d"),
           'datetime': datetime.now().strftime("%Y-%m-%d (%H:%M:%S)")}
    # send_email_LEAVE(email=, line_id=, id=)
    try:
        user_LEAVE_approve = employee.objects.get(employee_ID=str(id))
        data = json.loads(user_LEAVE_approve.activity_text)
        data.append(obj)
        user_LEAVE_approve.activity_text = json.dumps(data, ensure_ascii=False)
        user_LEAVE_approve.active_status = 'LEAVE'
        user_LEAVE_approve.save()
        connection.close()
        context={'data': 'Leave request'}
        return render(request, 'myworkplace/test.html',context )
    except MultipleObjectsReturned:
        print('ERROR LEAVE_approve duplicate id: {}'.format(id))
        remove_emp_id(id)
        print('Remove LEAVE_approve duplicate id: {}'.format(id))


def get_employee_profile(id):
    url = "https://idm.pea.co.th/webservices/EmployeeServices.asmx?WSDL"
    headers = {'content-type': 'text/xml'}
    xmltext = '''<?xml version="1.0" encoding="utf-8"?>
                <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                <soap:Body>
                    <GetEmployeeInfoByEmployeeId_SI xmlns="http://idm.pea.co.th/">
                    <WSAuthenKey>{0}</WSAuthenKey>
                    <EmployeeId>{1}</EmployeeId>
                    </GetEmployeeInfoByEmployeeId_SI>
                </soap:Body>
                </soap:Envelope>'''
    wsauth = 'e7040c1f-cace-430b-9bc0-f477c44016c3'
    body = xmltext.format(wsauth, "{}".format(id))
    res = requests.post(url, data=body, headers=headers, timeout=1, allow_redirects=True)
    o = xmltodict.parse(res.text)
    jsonconvert = dict(o)
    # print(jsonconvert)
    authData = jsonconvert["soap:Envelope"]['soap:Body']['GetEmployeeInfoByEmployeeId_SIResponse'][
        'GetEmployeeInfoByEmployeeId_SIResult']['ResultObject']

    return authData.get("FirstName"), authData.get("LastName"), authData.get("DepartmentShort"), \
           authData.get("PositionDescShort"), authData.get("LevelDesc"), authData.get("Gender")

def test(request):
    return render(request, 'myworkplace/test.html')

def remove_duplicate_all(request):
    context={'data1':[],
             'data2':[]}              
    for line_id in employee.objects.values_list('employee_line_ID', flat=True).distinct():
        context['data1'].append(employee.objects.filter(employee_line_ID=line_id).values_list(flat=True ))
        employee.objects.filter(pk__in=employee.objects.filter(employee_line_ID=line_id).values_list('id', flat=True )[1:]).delete()
        connection.close()
        context['data2'].append(employee.objects.filter(pk__in=employee.objects.filter(employee_line_ID=line_id).values_list('id', flat=True)))
    connection.close()
    return render(request,'myworkplace/removeid.html', context)

def remove_emp_id(emp_id):
    employee.objects.filter(pk__in=employee.objects.filter(employee_ID=emp_id).values_list('id', flat=True )[1:]).delete()
    connection.close()

def remove_duplicate_emp_id(request, emp_id):
    context={'data1':[]}
    context['data1'].append(employee.objects.filter(employee_ID=emp_id))
    connection.close()
    if request.method == "POST":
        remove_emp_id(emp_id)
        context = {'data1': []}
        context['data1'].append(employee.objects.filter(employee_ID=emp_id).__dict__)
        connection.close()
        return render(request, 'myworkplace/remove_duplicate_id.html', context)
    return render(request, 'myworkplace/remove_duplicate_id.html', context)

def remove_line_id(emp_line_id):
    employee.objects.filter(pk__in=employee.objects.filter(employee_line_ID=emp_line_id).values_list('id', flat=True)).delete()
    connection.close()

def remove_line_emp_id(request, emp_line_id):
    context={'data1':[],
             'data2':[]}
    context['data1'].append(employee.objects.filter(employee_line_ID=emp_line_id))
    connection.close()
    remove_line_id(emp_line_id)
    context['data2'].append(employee.objects.filter(employee_ID=emp_line_id))
    connection.close()
    return render(request, 'myworkplace/removeid.html', context)


def summarylist(request):
    context = {'date_data': "26/03/2020",
               'director': "นายเสริมชัย จา..",
                'position_dir': "อก."}
    return render(request, 'myworkplace/summary_list.html', context)


def summarylist1(request, dept_sap):
    context={'data':employee.objects.filter(employee_dept_sap=dept_sap)}
    return render(request, 'myworkplace/summary_list1.html', context)





def update_employee_profile(request):

    # user =employee.objects.get(employee_ID='233124')
    # print(user.employee_posi_text_short)
    # print(type(user.employee_posi_text_short))
    # print(user.employee_posi_text_short == None)
    # print(user.employee_posi_text_short == 'None')

    users = employee.objects.filter(employee_posi_text_short=None)
    total_num=len(users)
    i=1
    for item in users:
        print('{}/{}'.format(i,total_num))
        first_name, last_name, sex_desc, posi_text_short, dept_sap_short, dept_sap, dept_upper, sub_region, emp_email = get_user_email(
            item.employee_ID)
        item.employee_posi_text_short = posi_text_short
        item.employee_dept_sap_short = dept_sap_short
        item.employee_dept_sap = dept_sap
        item.employee_dept_upper = dept_upper
        item.employee_sub_region = sub_region
        item.employee_emp_email = emp_email
        item.save()
        i=i+1

    return render(request, 'myworkplace/home.html')