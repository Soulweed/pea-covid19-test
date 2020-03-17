from django.shortcuts import render, redirect
from .models import employee
import json
from datetime import datetime


# Create your views here.
def home(request):
    data1 = employee.objects.all()
    context = {'number_of_employee': len(data1)}
    return render(request, 'myworkplace/home.html', context)

def daily_update(request, id):
    print('access daily update')
    data=employee.objects.get(employee_ID=id).__dict__
    print(type(data))
    print(data)
    context = {'data': data}
    print(context)
    if request.method=="POST":
        activity = request.POST.get("activity")
        print(activity)

        health = activity

        user = employee.objects.get(employee_ID=id)
        print(user.__dict__)
        # user.update_activitiy({'data':activity})

        obj = {'type':'daily_update', 'health':health, 'datetime': datetime.now().strftime("%Y-%m-%d (%H:%M:%S)")}

        data = json.loads(user.activity_text)
        print(data)

        data.append(obj)
        print(data)
        user.activity_text = json.dumps(data)
        user.save()

    return render (request, 'myworkplace/daily_update.html', context)


def personal_info(request, id):
    print('access personal info')
    data=employee.objects.get(employee_line_ID=id).__dict__
    print(type(data))
    print(data)
    context = {'data': data}
    print(context)
    return render(request, 'myworkplace/personal_info.html', context)

def screen(request, id):
    data = employee.objects.get(employee_ID=id).__dict__
    context = {'data': data}
    if request.method=="POST":
        name = request.POST.get("input_name")
        workplace = request.POST.get("input_workplace")
        gender = request.POST.get("input_gender")
        age = request.POST.get("input_age")

        fever = request.POST.get("input_fever")
        cold = request.POST.get("input_cold")
        travel = request.POST.get("input_travel")
        travel_dangerous_area = request.POST.get("input_travel_dangerous_area")
        home_dangerous = request.POST.get("input_home_dangerous")
        meet_foreigner = request.POST.get("input_meet_foreigner")
        contact = request.POST.get("input_contact")
        if fever=='FALSE' and cold =='FALSE' and travel=='FALSE' and travel_dangerous_area=='FALSE' \
                and home_dangerous=='FALSE' and meet_foreigner=='FALSE' and contact=='FALSE':
            health ="normal ปกติ"
        elif travel=='TRUE' or travel_dangerous_area=='TRUE' \
                or home_dangerous=='TRUE' or meet_foreigner=='TRUE' or contact=='TRUE':
            health = 'High risk เสี่ยงสูง'
        else:
            health = 'Risk เสี่ยง'

        user = employee.objects.get(employee_ID=id)
        user.emplyee_name=name
        user.work=workplace
        user.employee_gender=gender
        user.employee_age=age

        obj = {'type':'first_screen', 'health':health, 'datetime': datetime.now().strftime("%Y-%m-%d (%H:%M:%S)")}

        data = json.loads(user.activity_text)
        # print(data)

        data.append(obj)
        # print(data)
        user.activity_text = json.dumps(data, ensure_ascii=False)
        user.save()
        context.update({'health':health})
        print('######################')

        print(context)
        return render(request, 'myworkplace/confirm_screen.html', context)
    print('----------------------')
    print(context)
    return render(request, 'myworkplace/screen.html', context)

def confirm_screen(request):

    return render(request, 'myworkplace/confirm_screen.html')


# API
from rest_framework import viewsets

from .serializers import QuestionSerializer
from .models import question


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = question.objects.all().order_by('question_text')
    serializer_class = QuestionSerializer






####line bot#####

from django.http import HttpResponseForbidden, HttpResponse
from django.views.decorators.csrf import csrf_exempt


from rest_framework import viewsets
# from applicant.models import employee, participant
#
# from applicant.serializers import EmployeeSerializer

from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (
    MessageEvent,
    TextMessage,
    TextSendMessage,
)
import os

# YOUR_CHANNEL_ACCESS_TOKEN = os.environ["Ga+IdjcgPa032XLB5IaBPG2Fk+1VLs1+Lc+KFmbSjJXLZK+9RTT3+oyxqd9dG0dejJQ0a8LHz8dk8uXj6WJ/XjXpZzWRz9qRYyQNiOXwPbi7qa16vCYm1UwgL5mHF3j/Rk7ca5oxnKshQIyUizbQlwdB04t89/1O/w1cDnyilFU="]
# YOUR_CHANNEL_SECRET = os.environ["ada0193e1d7e79a4aa93a938b9300246"]

YOUR_CHANNEL_ACCESS_TOKEN="O9WalOm/R+TB7PdDOli1Bg20ZTEIWL4VdoDQFHbRPP2TWafBO/Xf+V7lq2oT/7AsRX+ILQK6FwcU6r+e69Ca/b0veDKZc0mp9cw+/Y4pkAWL9Wu8sX6Ospg4jzzs0Wwpdt27QjN9KjdjDoE8ljgn5AdB04t89/1O/w1cDnyilFU="

YOUR_CHANNEL_SECRET="3159d75a7c0f34bf72a9609987675644"

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

# queryset = employee.objects.all().order_by('name')
# serializer_class = EmployeeSerializer
# print('print details')
# # print(queryset)


@csrf_exempt
def callback(request):
    print('Here is callback function')
    signature = request.META['HTTP_X_LINE_SIGNATURE']
    body = request.body.decode('utf-8')
    print(body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        HttpResponseForbidden()
    return HttpResponse('OK', status=200)

def gen_DU_form(request):
    pass


reply_text='A whole new world'
# # オウム返し
@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    print('Here is handle_text_message function')
    dict_event=event.__dict__
    # print(dict_event)
    dict_source=dict_event['source'].__dict__
    dict_message=dict_event['message'].__dict__
    # print(dict_message['text'])

    if dict_message['text']=='บันทึกสุขภาพ':
        employee_Line_ID_list = [x.employee_line_ID for x in employee.objects.all()]
        user_employee = employee.objects.get(employee_line_ID=dict_source['user_id'])
        print(user_employee)
        if dict_source['user_id'] in employee_Line_ID_list:
            line_bot_api.reply_message(event.reply_token,
                                       TextSendMessage(text='www.https://pea-covid19-test.herokuapp.com/daily_update/{}/'.format(user_employee.employee_ID)))
        else:
            line_bot_api.reply_message(event.reply_token,
                                       TextSendMessage(text='คุณยังไม่ได้ลงทะเบียน กรุณาป้อนรหัสพนักงาน 6 หลัก'))
    elif dict_message['text']=='test':

        {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "image",
                        "url": "https://sv1.picz.in.th/images/2020/03/16/Qt1zb2.png",
                        "size": "full",
                        "aspectMode": "cover",
                        "aspectRatio": "1:1",
                        "gravity": "center"
                    },
                    {
                        "type": "image",
                        "url": "https://sv1.picz.in.th/images/2020/03/16/Qt1zb2.png",
                        "position": "absolute",
                        "aspectMode": "fit",
                        "aspectRatio": "1:1",
                        "offsetTop": "0px",
                        "offsetBottom": "0px",
                        "offsetStart": "0px",
                        "offsetEnd": "0px",
                        "size": "full"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "ระดับความเสี่ยง",
                                "size": "lg"
                            },
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "เสี่ยงมาก",
                                        "size": "4xl",
                                        "align": "center",
                                        "offsetStart": "20px"
                                    },
                                    {
                                        "type": "image",
                                        "url": "https://sv1.picz.in.th/images/2020/03/17/Qw4M9N.png",
                                        "size": "xs"
                                    }
                                ],
                                "margin": "lg"
                            },
                            {
                                "type": "separator",
                                "color": "#111111",
                                "margin": "lg"
                            },
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                            {
                                                "type": "text",
                                                "text": "คะแนนความ",
                                                "size": "xl",
                                                "weight": "bold"
                                            },
                                            {
                                                "type": "text",
                                                "text": "ตระหนักโรค",
                                                "size": "xl",
                                                "weight": "bold"
                                            }
                                        ]
                                    },
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                            {
                                                "type": "text",
                                                "text": "4",
                                                "size": "4xl",
                                                "align": "end"
                                            }
                                        ]
                                    }
                                ],
                                "margin": "md"
                            },
                            {
                                "type": "separator",
                                "color": "#111111"
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "บันทึกสุขภาพประจำวัน",
                                        "size": "md"
                                    },
                                    {
                                        "type": "text",
                                        "text": "2020-03-06",
                                        "size": "md"
                                    },
                                    {
                                        "type": "text",
                                        "text": "บันทึกแล้ว",
                                        "size": "lg",
                                        "weight": "bold",
                                        "style": "italic"
                                    }
                                ],
                                "margin": "md"
                            }
                        ],
                        "position": "absolute",
                        "offsetStart": "20px",
                        "offsetTop": "10px"
                    }
                ],
                "paddingAll": "0px",
                "position": "relative"
            }
        }


    elif dict_message['text']=='ข้อมูลส่วนตัว':
        employee_Line_ID_list = [x.employee_line_ID for x in employee.objects.all()]
        user_employee = employee.objects.get(employee_line_ID=dict_source['user_id'])
        print(user_employee)
        if dict_source['user_id'] in employee_Line_ID_list:
            line_bot_api.reply_message(event.reply_token,
                                       TextSendMessage(text='www.https://pea-covid19-test.herokuapp.com/personal_info/{}/'.format(user_employee.employee_line_ID)))
        else:
            line_bot_api.reply_message(event.reply_token,
                                       TextSendMessage(text='คุณยังไม่ได้ลงทะเบียน กรุณาป้อนรหัสพนักงาน 6 หลัก'))

    elif dict_message['text'].isnumeric() and len(dict_message['text'])==6: # check is number
        employee_Line_ID_list =[x.employee_line_ID for x in employee.objects.all()]

        if dict_source['user_id'] not in employee_Line_ID_list:  # check new customer
            obj = [{'type':'register', 'datetime':datetime.now().strftime("%Y-%m-%d (%H:%M:%S)")}]

            new_user = employee(emplyee_name='blank', employee_line_ID=dict_source['user_id'],
                                employee_ID=dict_message['text'], activity_text=json.dumps(obj), quarantined=False, infected=False)
            new_user.save()
            line_bot_api.reply_message(event.reply_token,
                                       TextSendMessage(text='ระบบได้ลงทะเบียนรหัสพนักงานสำเร็จ '
                                                            'กรุณากรอกแบบฟอร์มคัดกรอง www.https://pea-covid19-test.herokuapp.com/screen/{}/'.format(new_user.employee_ID)))

            # ส่งคำถามคัดกรอง

        else:  # existing customer
            line_bot_api.reply_message(event.reply_token,
                                       TextSendMessage(text='ไม่สามารถลงทะเบียนได้ไลน์ไอดีนี้ได้ลงทะเบียนแล้ว หากสงสัยติดต่อ admin'))
    else:
        line_bot_api.reply_message(event.reply_token,
                                           TextSendMessage(text='ระบบยังไม่เสร็จตอนนี้ หากต้องการลงทพเบียน'
                                                                'กรุณากรอกเลขรหัสพนักงาน 6 หลัก'))

    # else: # existing customer
    #     if dict_message['text']=='บริการพิเศษ':
    #         line_bot_api.reply_message(event.reply_token,
    #                                    TextSendMessage(text='working on it บริการพิเศษ'))
    #
    #     else:
    #         line_bot_api.reply_message(event.reply_token,
    #                                    TextSendMessage(text='กรุณากรอกเลขรหัสพนักงาน 6 หลัก'))

