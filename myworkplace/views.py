from django.shortcuts import render, redirect
from django.db import connection
from .models import employee, question, emailemployee
from send_email.views import send_email_wfh_request
import json
from datetime import datetime, timedelta, date
import getpass
from collections import defaultdict
from exchangelib import Configuration, Account, DELEGATE, Credentials
from exchangelib import Message, Mailbox, FileAttachment
import base64
import requests, xmltodict
import random


# importing email library
from django.core.mail import send_mail
from django.conf import settings
from send_email.views import send_email_register, get_user_email, send_email_wfh14day_request, send_email_confrim_register, \
    send_email_meetdoc_request, send_email_confrim_wfh



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
        user = employee.objects.get(employee_ID=id)
        data = json.loads(user.activity_daily_update)
        data.append(obj)
        user.activity_daily_update = json.dumps(data)
        user.healthy=health
        user.daily_update=True
        user.save()
        connection.close()
        if health == 'normal':
            return redirect(normal1, id)
        elif health == 'flu':
            return redirect(normal2, id)
        elif health =='quarantine':
            return redirect(quarantine, id)
        elif health =='hospital':
            return redirect(meet_doc2, id)
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
            # print(page)
            # print("OK2")
            id_boss = request.POST.get("id_boss")
            total_day = 14
            startdate=(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

            enddate=(datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d")
            # print(id_boss)
            email = get_user_email(id_boss)
            # print(email)

            FirstName, LastName, DepartmentShort, PositionDescShort, LevelDesc , Gender= get_employee_profile(
                id_boss)
            context={'id_boss': id_boss, 'email_boss': email, 'total_day': total_day,'startdate':startdate, 'enddate':enddate,
                            'boss_name': '{} {}'.format(FirstName, LastName), 'JobDesc': PositionDescShort, 'Gender':Gender}
            return render(request, 'myworkplace/formleave3.html', context)

        if (page == "3"):
            # print("OK3")
            email = request.POST.get("email_boss")  #เอา email จาก ที่ซ่อนใว้ใน hidden ใน formleave3


            startdate=(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

            enddate=(datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d")
            obj = {'type': 'wfh14days_request', 'startdate': startdate, 'enddate':enddate,
                   'datetime': datetime.now().strftime("%Y-%m-%d (%H:%M:%S)")}

            user = employee.objects.get(employee_ID=str(id))
            data = json.loads(user.activity_text)
            data.append(obj)
            user.activity_text = json.dumps(data, ensure_ascii=False)
            user.approved_status = 'Leave'
            user.save()
            connection.close()
            send_email_wfh14day_request(id=id, email_boss=email, name=user.emplyee_name, startdate=startdate, enddate=enddate)
            return render(request, 'myworkplace/formleave4.html', context)

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
            # print('startdate: ', get_startdate)
            # print(type(get_startdate))
            # print('enddate ', get_enddate)
            # print(type(get_enddate))
            startdate = datetime.strptime(get_startdate, "%Y-%m-%d").date()
            enddate = datetime.strptime(get_enddate, "%Y-%m-%d").date()
            delta = enddate - startdate
            total_date = delta.days + 1
            # print('total date', total_date)
            email = get_user_email(id_boss)
            FirstName, LastName, DepartmentShort, PositionDescShort, LevelDesc, Gender = get_employee_profile(
                id_boss)
            context={'Boss_name':'{} {}'.format(FirstName, LastName), 'Boss_position':PositionDescShort, 'Gender':Gender,
                     'startdate':get_startdate, 'enddate':get_enddate, 'total_date':total_date, 'email_boss': email}
            # print(context)
            return render(request, 'myworkplace/formwfh3.html', context)
        if (page=="2"):
            email = request.POST.get("email_boss")  #เอา email จาก ที่ซ่อนใว้ใน hidden ใน formleave3
            get_total_date =request.POST.get("total_date")
            get_startdate =request.POST.get("startdate")
            get_enddate =request.POST.get("enddate")
            obj = {'type': 'wfh_request', 'startdate': get_startdate, 'enddate':get_enddate,
                   'datetime': datetime.now().strftime("%Y-%m-%d (%H:%M:%S)")}

            user = employee.objects.get(employee_ID=str(id))
            data = json.loads(user.activity_text)
            data.append(obj)
            user.activity_text = json.dumps(data, ensure_ascii=False)
            user.approved_status = 'WFH'
            user.WFH_start_date=get_startdate
            user.WFH_end_date=get_enddate
            user.save()
            connection.close()
            send_email_wfh_request(id=id, email_boss=email, total_date=get_total_date, name=user.emplyee_name, startdate=get_startdate, enddate=get_enddate)

            return render(request, 'myworkplace/formwfh4.html')
    return render(request, 'myworkplace/formwfh2drange.html', context)

def meet_doc2(request,id):
    context = {'id':id}
    if request.method == 'POST':
        page = request.POST.get('page')
        if(page == "1"):

            id_boss = request.POST.get("director")
            email = get_user_email(id_boss)

            startdate=(datetime.now() + timedelta(days=1)).strftime("%Y/%m/%d")

            enddate=(datetime.now() + timedelta(days=15)).strftime("%Y/%m/%d")
            obj = {'type': 'meet_doc_request', 'startdate': startdate, 'enddate':enddate,
                   'datetime': datetime.now().strftime("%Y/%m/%d (%H:%M:%S)")}
            user = employee.objects.get(employee_ID=str(id))
            data = json.loads(user.activity_text)
            data.append(obj)
            user.activity_text = json.dumps(data, ensure_ascii=False)
            user.active_status = 'LEAVE'
            user.approved_status = 'Idle'
            user.LEAVE_start_date=startdate
            user.LEAVE_end_date=enddate
            user.save()
            connection.close()
            send_email_meetdoc_request(id=id, email_boss=email, name=user.emplyee_name )

        return render(request, 'myworkplace/formseedoc3.html', context)
    return render(request, 'myworkplace/formseedoc2.html', context)


def personal_info(request, id):
    data = employee.objects.get(employee_line_ID=id).__dict__
    context = {'data': data}
    connection.close()
    return render(request, 'myworkplace/personal_info.html', context)


def checkin(request, id):
    user = employee.objects.get(employee_ID=str(id))
    context = {'data': user.__dict__}

    if request.method == "POST":
        action_type = request.POST.get("type")
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")

        if(action_type == "checkin"):
            obj = {'type': action_type, 'latitude': latitude, 'longitude': longitude,
                   'datetime': datetime.now().strftime("%Y-%m-%d (%H:%M:%S)")}
            data = json.loads(user.activity_checkin)
            data.append(obj)
            user.activity_checkin = json.dumps(data, ensure_ascii=False)
            user.save()
            connection.close()
            return redirect(tscheckin, obj['datetime'])
        elif(action_type == "checkout"):
            obj = {'type': action_type, 'latitude': latitude, 'longitude': longitude,
                   'datetime': datetime.now().strftime("%Y-%m-%d (%H:%M:%S)")}
            data = json.loads(user.activity_checkout)
            data.append(obj)
            user.activity_checkout = json.dumps(data, ensure_ascii=False)
            user.save()
            connection.close()
            return redirect(tscheckout, obj['datetime'])
    return render(request, 'myworkplace/timestamp.html', context)



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
        return redirect(formwfh2, id)
    return render(request, 'myworkplace/normal1.html')

def normal2(request, id):
    if request.method == "POST":
        return redirect(formwfh2, id)
    return render(request, 'myworkplace/normal2.html')

def resultscreen2(request):
    return render(request, 'myworkplace/resultscreen2.html')

def resultscreen3(request):
    return render(request, 'myworkplace/resultscreen3.html')

def quarantine(request,id):
    if request.method == "POST":
        return redirect(LEAVE_request, id)
    return render(request, 'myworkplace/quarantine.html')

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
    try:
        user=employee.objects.get(employee_line_ID=line_id)
        connection.close()
        return redirect(home)
    except:
        FirstName, LastName, DepartmentShort, PositionDescShort, LevelDesc, Gender= get_employee_profile(emp_id)

        context ={'EmployeeID': emp_id, 'FirstName':FirstName, 'LastName':LastName, 'DepartmentShort':DepartmentShort,
                  'PositionDescShort':PositionDescShort, 'LevelDesc':LevelDesc, 'Gender':Gender}

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
            emp_name = request.POST.get("first-last name")
            ext = request.POST.get("ext")  # หมายเลขโทรศัพท์ภายใน
            mobile_phone = request.POST.get("mobile_phone")  # หมายเลขโทรศัพท์มือถือ
            building = request.POST.get("building")  # อาคาร
            floor = request.POST.get("floor")  # ชั้น
            address = request.POST.get("address")
            selector = request.POST.get("selector")
            addition_address = request.POST.get("addition_address")
            firstname_ref_1 = request.POST.get("firstname_ref_1")
            lastname_ref_1 = request.POST.get("lastname_ref_1")
            mobile_ref_1 = request.POST.get("mobile_ref_1")
            relation_ref_1 = request.POST.get("relation_ref_1")
            firstname_ref_2 = request.POST.get("firstname_ref_2")
            lastname_ref_2 = request.POST.get("lastname_ref_2")
            mobile_ref_2 = request.POST.get("mobile_ref_2")
            relation_ref_2 = request.POST.get("relation_ref_2")
            firstname_ref_3 = request.POST.get("firstname_ref_3")
            lastname_ref_3 = request.POST.get("lastname_ref_3")
            mobile_ref_3 = request.POST.get("mobile_ref_3")
            relation_ref_3 = request.POST.get("relation_ref_3")

            obj = {'type': 'register', 'datetime': datetime.now().strftime("%Y-%m-%d (%H:%M:%S)")}

            user_data = employee(
                emplyee_name='{} {}'.format(FirstName, LastName),
                employee_ID=emp_id,
                employee_line_ID=line_id,
                activity_text=json.dumps([obj], ensure_ascii=False),
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
                # emergency_one_first_name=firstname_ref_2,
                # emergency_one_last_name=lastname_ref_2,
                # emergency_one_tel=mobile_ref_2,
                # emergency_one_relationship=relation_ref_2,
                # emergency_two_first_name=firstname_ref_3,
                # emergency_two_last_name=lastname_ref_3,
                # emergency_two_tel=mobile_ref_3,
                # emergency_two_relationship=relation_ref_3,

            )
            user_data.save()
            print('model save: {}'.format(emp_id))
            connection.close()
            emp_email = get_user_email(emp_id)
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
        user = employee.objects.get(employee_ID=str(id))
        data = json.loads(user.activity_challenge)
        data.append(obj)
        user.activity_text = json.dumps(data, ensure_ascii=False)
        user.save()
        connection.close()
        if (answer == correct):
            return render(request, 'myworkplace/correct.html')
        else:
            return render(request, 'myworkplace/wrong.html')
    return render(request, 'myworkplace/challenge2.html', context)

def wrong(request):
    return render(request, 'myworkplace/wrong.html')

def correct(request):
    return render(request, 'myworkplace/correct.html')

def miss3d_du(request, id):
    data = employee.objects.get(employee_ID=str(id)).__dict__
    context = {'data': data}
    connection.close()
    return render(request, 'myworkplace/miss3d_du_id.html', context)


def miss3d_ts(request, id):
    data = employee.objects.get(employee_ID=str(id)).__dict__
    context = {'data': data, 'number':40}
    connection.close()

    return render(request, 'myworkplace/miss3d_ts_id.html', context)

# def WFH_request(request, id, boss):
#     day=10
#     obj = {'type': 'WFH_request', 'approved_by': boss,
#            'start_date': (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
#            'finish_date': (datetime.now() + timedelta(days=int(day))).strftime("%Y-%m-%d"),
#            'datetime': datetime.now().strftime("%Y-%m-%d (%H:%M:%S)")}
#
#     send_email_wfh_request(id=id, boss=boss)
#     user = employee.objects.get(employee_ID=str(id))
#     data = json.loads(user.activity_text)
#     data.append(obj)
#     user.activity_text = json.dumps(data, ensure_ascii=False)
#     user.approved_status = 'WFH'
#     user.save()
#     connection.close()
#     context = {'data': 'WFH request'}
#     return render(request, 'myworkplace/test.html', context)


def WFH_approve(request, id, boss, total_date):

    obj = {'type': 'WFH_approved', 'approved_by': boss,
           'start_date': (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
           'finish_date': (datetime.now() + timedelta(days=int(total_date))).strftime("%Y-%m-%d"),
           'datetime': datetime.now().strftime("%Y-%m-%d (%H:%M:%S)")}

    user = employee.objects.get(employee_ID=str(id))
    data = json.loads(user.activity_text)
    data.append(obj)
    user.activity_text = json.dumps(data, ensure_ascii=False)
    user.active_status='WFH'
    user.approved_status='Idle'
    user.save()
    connection.close()

    emp_email = get_user_email(id)
    send_email_confrim_wfh(boss=boss, emp_email=emp_email)
    return render(request, 'myworkplace/test2.html')


def LEAVE_approve(request, id, boss):
    day=14
    obj = {'type': 'LEAVE_request', 'approved_by': boss,
           'start_date': (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
           'finish_date': (datetime.now() + timedelta(days=int(day))).strftime("%Y-%m-%d"),
           'datetime': datetime.now().strftime("%Y-%m-%d (%H:%M:%S)")}
    # send_email_LEAVE(email=, line_id=, id=)
    user = employee.objects.get(employee_ID=str(id))
    data = json.loads(user.activity_text)
    data.append(obj)
    user.activity_text = json.dumps(data, ensure_ascii=False)
    user.active_status = 'LEAVE'
    user.save()
    user.close()
    context={'data': 'Leave request'}
    return render(request, 'myworkplace/test.html',context )



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

def removeid(request):
    context={'data1':[],
             'data2':[]}
    # for line_id in employee.objects.values_list('employee_line_ID', flat=True).distinct():
    #     # Email.objects.filter( pk__in=Email.objects.filter( email=email ).values_list('id', flat=True)[1:] ).delete()
    #     employee.objects.filter()
    #     context['data'].append(line_id)
    # for item in employee.objects.filter(employee_line_ID='U31b86969da2b249fcfb30164065d513b'):
    #     context['data'].append(item)

    for line_id in employee.objects.values_list('employee_line_ID', flat=True).distinct():
        context['data1'].append(employee.objects.filter(employee_line_ID=line_id).values_list(flat=True ))
        employee.objects.filter(pk__in=employee.objects.filter(employee_line_ID=line_id).values_list('id', flat=True )[1:]).delete()
        context['data2'].append(employee.objects.filter(pk__in=employee.objects.filter(employee_line_ID=line_id).values_list('id', flat=True)))
    connection.close()
    return render(request,'myworkplace/removeid.html', context)
