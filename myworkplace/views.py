from django.shortcuts import render, redirect
from .models import employee
import json
from datetime import datetime, timedelta
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


# Create your views here.
def home(request):

    context = {'number_of_employee': employee.objects.count(),
               'high_risk':20, 'normal_wfh':30, 'risk_wfh':10, 'pea_office':30, 'no_daily_update':40}
    print(context)
    return render(request, 'myworkplace/home.html', context)

def daily_update(request, id):
    user = employee.objects.get(employee_ID=str(id))
    context = {'data': user.__dict__
               }
    if request.method == "POST":
        fever = request.POST.get("id_fever")
        cold = request.POST.get("id_cold")
        contact_foreigner = request.POST.get("id_contact_foreigner")
        travel_to_infected_area = request.POST.get("id_travel_to_infected_area")
        live_with_risk_person = request.POST.get("id_live_with_risk_person")
        contact_with_risk = request.POST.get("id_contact_with_risk")

        if fever == 'FALSE' and cold == 'FALSE' and contact_foreigner == 'FALSE' and travel_to_infected_area == 'FALSE' \
                and live_with_risk_person == 'FALSE' and contact_with_risk == 'FALSE':
            health = "normal ปกติ"
        elif travel_to_infected_area == 'TRUE' or live_with_risk_person == 'TRUE' \
                or contact_with_risk == 'TRUE':
            health = 'High risk เสี่ยงสูง'
        else:
            health = 'Risk เสี่ยง'
        # user = employee.objects.get(employee_ID=id)
        obj = {'type': 'daily_update', 'health': health, 'datetime': datetime.now().strftime("%Y-%m-%d (%H:%M:%S)")}
        data = json.loads(user.activity_text)
        data.append(obj)
        user.activity_text = json.dumps(data)
        user.healthy=health
        user.save()
        return redirect(confirm, id)

    return render(request, 'myworkplace/daily_update.html', context)

def personal_info(request, id):
    print('access personal info')
    data = employee.objects.get(employee_line_ID=id).__dict__
    print(type(data))
    print(data)
    context = {'data': data}
    print(context)
    return render(request, 'myworkplace/personal_info.html', context)

def screen(request, id):
    data = employee.objects.get(employee_ID=str(id)).__dict__
    context = {'data': data}

    if request.method == "POST":
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

        if fever == 'FALSE' and cold == 'FALSE' and travel == 'FALSE' and travel_dangerous_area == 'FALSE' \
                and home_dangerous == 'FALSE' and meet_foreigner == 'FALSE' and contact == 'FALSE':
            health = "normal ปกติ"
        elif travel == 'TRUE' or travel_dangerous_area == 'TRUE' \
                or home_dangerous == 'TRUE' or meet_foreigner == 'TRUE' or contact == 'TRUE':
            health = 'High risk เสี่ยงสูง'
        else:
            health = 'Risk เสี่ยง'

        user = employee.objects.get(employee_ID=id)
        user.emplyee_name = name
        user.work = workplace
        user.employee_gender = gender
        user.employee_age = age
        user.healthy = health

        obj = {'type': 'first_screen', 'health': health, 'datetime': datetime.now().strftime("%Y-%m-%d (%H:%M:%S)")}
        data = json.loads(user.activity_text)
        # print(data)

        data.append(obj)
        # print(data)
        user.activity_text = json.dumps(data, ensure_ascii=False)
        user.save()
        context.update({'health': health})
        print('######################')

        print(context)
        if health == "normal ปกติ":
            return redirect(normal_group, id)
        elif health == 'Risk เสี่ยง':
            return redirect(medium_group, id)
        else:
            return redirect(risk_form, id)
        # return render(request, 'myworkplace/confirm.html', context)
    print('----------------------')
    print(context)
    return render(request, 'myworkplace/screen.html', context)

def checkin(request, id):
    data = employee.objects.get(employee_ID=str(id)).__dict__
    context = {'data': data}

    if request.method == "POST":
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")
        print('##########-----------##########')
        print('latitute is', latitude)
        obj = {'type': 'checkin', 'latitude': latitude, 'longitude': longitude,
               'datetime': datetime.now().strftime("%Y-%m-%d (%H:%M:%S)")}

        user = employee.objects.get(employee_ID=str(id))
        data = json.loads(user.activity_text)
        data.append(obj)
        print(data)
        user.activity_text = json.dumps(data, ensure_ascii=False)
        user.save()
        context['data'].update({'datetime': obj['datetime']})
        return render(request, 'myworkplace/checkinComplete.html', context)

    return render(request, 'myworkplace/checkin.html', context)

def challenge(request, id):
    data = employee.objects.get(employee_ID=id).__dict__
    context = {'data': data}

    if request.method == "POST":
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")
        print('##########-----------##########')
        print('latitute is', latitude)
        obj = {'type': 'question', 'latitude': latitude, 'longitude': longitude,
               'datetime': datetime.now().strftime("%Y-%m-%d (%H:%M:%S)")}

        user = employee.objects.get(employee_ID=str(id))
        data = json.loads(user.activity_text)
        data.append(obj)
        print(data)
        user.activity_text = json.dumps(data, ensure_ascii=False)
        user.save()
        context['data'].update({'datetime': obj['datetime']})
        return render(request, 'myworkplace/checkinComplete.html', context)

    return render(request, 'myworkplace/challenge2.html', context)

def normal_group(request, id):
    data = employee.objects.get(employee_ID=id).__dict__
    context = {'data': data}
    if request.method == "POST":
        print('here we are')
        print('send email')  # send email
        start_date = request.POST.get("id_start_date")
        end_date = request.POST.get("id_end_date")
        total_date = request.POST.get("id_total_date")
        employee_up1 = request.POST.get("id_employee_up1")
        employee_up2 = request.POST.get("id_employee_up2")
        customRadio = request.POST.get("customRadio")

        print(start_date, end_date, total_date, employee_up1, employee_up2)

        ######send email here#########
        if (customRadio == 'Accept'):
            print(id)
            print(employee_up1)
            print(employee_up2)

        return redirect(confirm, id)
    print('----------------------')
    print(context)
    return render(request, 'myworkplace/normal_group.html', context)

def medium_group(request, id):
    data = employee.objects.get(employee_ID=id).__dict__
    context = {'data': data}
    if request.method == "POST":
        print('here we are')
        print('send email')  # send email

        return redirect(confirm, id)
    print('----------------------')
    print(context)
    return render(request, 'myworkplace/medium_group.html', context)

def risk_group(request, id):
    data = employee.objects.get(employee_ID=id).__dict__
    print('risk group')
    context = {'data': data}
    if request.method == "POST":
        print('here we are')
        print('send email')  # send email
        ######send email here#########
        # user = employee.objects.get(employee_ID=id).__dict__
        # user.infected == True
        # user.save()
        return redirect(confirm, id)
    print('----------------------')
    print(context)
    return render(request, 'myworkplace/risk_group.html', context)

def risk_form(request, id):
    data = employee.objects.get(employee_ID=id).__dict__
    print('risk form')
    context = {'data': data}
    if request.method == "POST":
        print('here we are')
        ######send email here#########
        print('risk form')

        return redirect(risk_group, id)
    print('----------------------')
    print(context)
    return render(request, 'myworkplace/risk_form.html', context)

def confirm(request, id):
    user = employee.objects.get(employee_ID=id)
    context = {'id': user.employee_ID, 'health': user.healthy}
    return render(request, 'myworkplace/confirm.html', context)

def confirm_WFH(request, id):
    print('link to work form home confirm page')
    return render(request, 'myworkplace/confirm_WFH.html')


# API
from rest_framework import viewsets
from .serializers import QuestionSerializer
from .models import question


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = question.objects.all().order_by('question_text')
    serializer_class = QuestionSerializer


####line bot#####

# from django.http import HttpResponseForbidden, HttpResponse
# from django.views.decorators.csrf import csrf_exempt
#
# from rest_framework import viewsets
# # from applicant.models import employee, participant
# #
# # from applicant.serializers import EmployeeSerializer
#
# from linebot import (LineBotApi, WebhookHandler)
# from linebot.exceptions import (InvalidSignatureError)
# from linebot.models import (
#     MessageEvent,
#     TextMessage,
#     TextSendMessage,
#     FlexSendMessage,
#     ImageSendMessage,
# )
#
# import os
#
# # YOUR_CHANNEL_ACCESS_TOKEN = os.environ["Ga+IdjcgPa032XLB5IaBPG2Fk+1VLs1+Lc+KFmbSjJXLZK+9RTT3+oyxqd9dG0dejJQ0a8LHz8dk8uXj6WJ/XjXpZzWRz9qRYyQNiOXwPbi7qa16vCYm1UwgL5mHF3j/Rk7ca5oxnKshQIyUizbQlwdB04t89/1O/w1cDnyilFU="]
# # YOUR_CHANNEL_SECRET = os.environ["ada0193e1d7e79a4aa93a938b9300246"]
#
# YOUR_CHANNEL_ACCESS_TOKEN = "O9WalOm/R+TB7PdDOli1Bg20ZTEIWL4VdoDQFHbRPP2TWafBO/Xf+V7lq2oT/7AsRX+ILQK6FwcU6r+e69Ca/b0veDKZc0mp9cw+/Y4pkAWL9Wu8sX6Ospg4jzzs0Wwpdt27QjN9KjdjDoE8ljgn5AdB04t89/1O/w1cDnyilFU="
#
# YOUR_CHANNEL_SECRET = "3159d75a7c0f34bf72a9609987675644"
#
# line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
# handler = WebhookHandler(YOUR_CHANNEL_SECRET)
#
#
# # queryset = employee.objects.all().order_by('name')
# # serializer_class = EmployeeSerializer
# # print('print details')
# # # print(queryset)
#
#
# @csrf_exempt
# def callback(request):
#     print('Here is callback function')
#     signature = request.META['HTTP_X_LINE_SIGNATURE']
#     body = request.body.decode('utf-8')
#     print(body)
#     try:
#         handler.handle(body, signature)
#     except InvalidSignatureError:
#         HttpResponseForbidden()
#     return HttpResponse('OK', status=200)
#
# reply_text = 'A whole new world'
#
# # # オウム返し
# @handler.add(MessageEvent, message=TextMessage)
# def handle_text_message(event):
#     print('Here is handle_text_message function')
#     dict_event = event.__dict__
#     # print(dict_event)
#     dict_source = dict_event['source'].__dict__
#     dict_message = dict_event['message'].__dict__
#     # print(dict_message['text'])
#     if dict_message['text'].isnumeric() and (
#             len(dict_message['text']) == 6 or len(dict_message['text']) == 7):
#         ##### function create email กับ content ข้างใน
#         try:
#             employee.objects.get(employee_line_ID=dict_source['user_id'])
#             line_bot_api.reply_message(event.reply_token,
#                                        TextSendMessage(text='ท่านได้ลงทะเบียนแล้ว'))
#         except:
#             email_name = get_user_email(id=dict_message['text'])
#             print(email_name)
#             if email_name is not None:
#                 print('-----------------')
#                 print('here we are')
#                 try:
#                     send_email_register(email=email_name, line_id=dict_source['user_id'], id=dict_message['text'])
#                     line_bot_api.reply_message(event.reply_token,
#                                                TextSendMessage(
#                                                    text='กรุณายืนยันตัวตนในอีเมลของท่าน https://email.pea.co.th'),
#                                                    )
#                 except:
#                     line_bot_api.reply_message(event.reply_token,
#                                                TextSendMessage(text='ลองอีกครั้ง'))
#             else:
#                 line_bot_api.reply_message(event.reply_token,
#                                            [TextSendMessage(
#                                                text='ไปกรอกอีเมล์ใน IDM ด้วย http://idm.pea.co.th'),
#                                                ImageSendMessage(
#                                                    original_content_url='https://www.img.in.th/images/600a10b547eb587a9d42525edcce704f.jpg',
#                                                    preview_image_url='https://www.img.in.th/images/600a10b547eb587a9d42525edcce704f.jpg'
#                                                ),
#                                                ImageSendMessage(
#                                                    original_content_url='https://www.img.in.th/images/7ba36f03f09d94f2a8a692297e364db2.jpg',
#                                                    preview_image_url='https://www.img.in.th/images/7ba36f03f09d94f2a8a692297e364db2.jpg'
#                                                ),
#                                                ImageSendMessage(
#                                                    original_content_url='https://www.imag.in.th/images/031525e6dce37aa260bac21483c11522.jpg',
#                                                    preview_image_url='https://www.imag.in.th/images/031525e6dce37aa260bac21483c11522.jpg'
#                                                )
#                                            ])
#     else:
#         try:
#             user_employee = employee.objects.get(employee_line_ID=dict_source['user_id'])
#             if dict_message['text'] == 'leave':
#                 line_bot_api.reply_message(event.reply_token,
#                                            FlexSendMessage(
#                                                alt_text='hello',
#                                                contents={
#   "type": "carousel",
#   "contents": [
#     {
#       "type": "bubble",
#       "body": {
#         "type": "box",
#         "layout": "vertical",
#         "contents": [
#           {
#             "type": "image",
#             "size": "full",
#             "aspectMode": "cover",
#             "gravity": "center",
#             "aspectRatio": "1:1",
#             "url": "https://sv1.picz.in.th/images/2020/03/19/Qi9EIN.png"
#           },
#           {
#             "type": "image",
#             "url": "https://www.img9.in.th/images/2020/03/19/-WFHb1.png",
#             "aspectMode": "cover",
#             "size": "full",
#             "action": {
#               "type": "uri",
#               "label": "action",
#               "uri": "https://pea-covid19-test.herokuapp.com/normal_group/{}/".format(
#                                                                                user_employee.employee_ID)
#             },
#             "aspectRatio": "1040:174"
#           }
#         ],
#         "paddingAll": "0px"
#       }
#     },
#     {
#       "type": "bubble",
#       "body": {
#         "type": "box",
#         "layout": "vertical",
#         "contents": [
#           {
#             "type": "image",
#             "size": "full",
#             "aspectMode": "cover",
#             "gravity": "center",
#             "url": "https://sv1.picz.in.th/images/2020/03/19/Qi9wFu.png",
#             "aspectRatio": "1:1"
#           },
#           {
#             "type": "image",
#             "url": "https://sv1.picz.in.th/images/2020/03/19/Qi9Rqe.png",
#             "aspectMode": "cover",
#             "size": "full",
#             "aspectRatio": "1040:174",
#             "action": {
#               "type": "uri",
#               "label": "action",
#               "uri": "https://pea-covid19-test.herokuapp.com/risk_group/{}/".format(
#                                                                                user_employee.employee_ID)
#             }
#           }
#         ],
#         "paddingAll": "0px"
#       }
#     },
#     {
#       "type": "bubble",
#       "body": {
#         "type": "box",
#         "layout": "vertical",
#         "contents": [
#           {
#             "type": "image",
#             "size": "full",
#             "aspectMode": "cover",
#             "gravity": "center",
#             "aspectRatio": "1:1",
#             "url": "https://sv1.picz.in.th/images/2020/03/20/Qi6eD2.png"
#           },
#           {
#             "type": "image",
#             "url": "https://sv1.picz.in.th/images/2020/03/20/Qi6IED.png",
#             "aspectMode": "cover",
#             "size": "full",
#             "action": {
#               "type": "uri",
#               "label": "action",
#               "uri": "https://pea-covid19-test.herokuapp.com/"
#             },
#             "aspectRatio": "1040:174"
#           }
#         ],
#         "paddingAll": "0px"
#       }
#     }
#   ]
# }
#                                            )
#                                            )
#             elif dict_message['text'] == 'test':
#                 # print('ทดสอบ ส่งอีเมล')
#                 line_bot_api.reply_message(event.reply_token,
#                                            TextSendMessage(text='ทดสอบ'))
#                 # send_email_register(id = dict_message['text'], line_id=dict_source['user_id'])
#                 # print('ทดสอบ ส่งอีเมลแล้วเสร็จ')
#             elif dict_message['text'] == 'check':
#                 line_bot_api.reply_message(event.reply_token,
#                                            FlexSendMessage(
#                                                alt_text='hello',
#                                                contents={
#                                                    "type": "carousel",
#                                                    "contents": [
#                                                        {
#                                                            "type": "bubble",
#                                                            "body": {
#                                                                "type": "box",
#                                                                "layout": "vertical",
#                                                                "contents": [
#                                                                    {
#                                                                        "type": "image",
#                                                                        "size": "full",
#                                                                        "aspectMode": "cover",
#                                                                        "gravity": "center",
#                                                                        "url": "https://sv1.picz.in.th/images/2020/03/19/QgvtPI.png",
#                                                                        "aspectRatio": "1:1"
#                                                                    },
#                                                                    {
#                                                                        "type": "image",
#                                                                        "url": "https://sv1.picz.in.th/images/2020/03/19/QgvxrE.png",
#                                                                        "aspectMode": "cover",
#                                                                        "size": "full",
#                                                                        "aspectRatio": "1040:174",
#                                                                        "action": {
#                                                                            "type": "uri",
#                                                                            "label": "action",
#                                                                            "uri": "https://pea-covid19-test.herokuapp.com/daily_update/{}".format(
#                                                                                user_employee.employee_ID)
#                                                                        }
#                                                                    }
#                                                                ],
#                                                                "paddingAll": "0px"
#                                                            }
#                                                        },
#                                                        {
#                                                            "type": "bubble",
#                                                            "body": {
#                                                                "type": "box",
#                                                                "layout": "vertical",
#                                                                "contents": [
#                                                                    {
#                                                                        "type": "image",
#                                                                        "size": "full",
#                                                                        "aspectMode": "cover",
#                                                                        "gravity": "center",
#                                                                        "url": "https://sv1.picz.in.th/images/2020/03/19/QgLwmJ.png",
#                                                                        "aspectRatio": "1:1"
#                                                                    },
#                                                                    {
#                                                                        "type": "image",
#                                                                        "url": "https://sv1.picz.in.th/images/2020/03/19/QgLts9.png",
#                                                                        "aspectMode": "cover",
#                                                                        "size": "full",
#                                                                        "aspectRatio": "1040:174",
#                                                                        "action": {
#                                                                            "type": "uri",
#                                                                            "label": "action",
#                                                                            "uri": "https://pea-covid19-test.herokuapp.com/challenge2/{}/".format(user_employee.employee_ID)
#                                                                        }
#                                                                    }
#                                                                ],
#                                                                "paddingAll": "0px"
#                                                            }
#                                                        }
#                                                    ]
#                                                }
#                                            ))
#             elif dict_message['text'] == 'profile':
#                 line_bot_api.reply_message(event.reply_token,
#                                            FlexSendMessage(
#                                                alt_text='hello',
#                                                contents={
#   "type": "bubble",
#   "hero": {
#     "type": "image",
#     "url": "https://sv1.picz.in.th/images/2020/03/19/QiOkcu.png",
#     "size": "full",
#     "action": {
#       "type": "uri",
#       "uri": "http://linecorp.com/"
#     },
#     "aspectMode": "cover",
#     "aspectRatio": "1040:677"
#   },
#   "body": {
#     "type": "box",
#     "layout": "vertical",
#     "contents": [
#       {
#         "type": "text",
#         "text": "นายภาคภูมิ ประเสริฐ",
#         "weight": "bold",
#         "size": "xl",
#         "align": "center"
#       },
#         {
#             "type": "text",
#             "text": "{}".format(user_employee.employee_ID),
#             "align": "center",
#             "size": "xl",
#             "weight": "bold"
#         },
#       {
#         "type": "box",
#         "layout": "horizontal",
#         "contents": [
#           {
#             "type": "text",
#             "text": "ความเสี่ยง :",
#             "size": "xl"
#           },
#           {
#             "type": "text",
#             "text": "แยกตัว",
#             "size": "xl"
#           }
#         ],
#         "margin": "md"
#       },
#       {
#         "type": "box",
#         "layout": "horizontal",
#         "contents": [
#           {
#             "type": "text",
#             "text": "สถานะ :",
#             "size": "xl"
#           },
#           {
#             "type": "text",
#             "text": "เฝ้าระวัง",
#             "size": "xl"
#           }
#         ],
#         "margin": "sm"
#       },
#       {
#         "type": "box",
#         "layout": "horizontal",
#         "contents": [
#           {
#             "type": "text",
#             "text": "วันที่ประเมิน :",
#             "size": "xl"
#           },
#           {
#             "type": "text",
#             "text": "19 มี.ค. 63",
#             "size": "xl"
#           }
#         ],
#         "margin": "sm"
#       },
#       {
#         "type": "box",
#         "layout": "horizontal",
#         "contents": [
#           {
#             "type": "text",
#             "text": "เวลา",
#             "size": "xl",
#             "align": "start"
#           },
#           {
#             "type": "text",
#             "text": "10:30 น.",
#             "size": "xl"
#           }
#         ],
#         "margin": "sm"
#       },
#       {
#         "type": "box",
#         "layout": "horizontal",
#         "contents": [
#           {
#             "type": "text",
#             "text": "เหลือเวลา",
#             "size": "xl"
#           },
#           {
#             "type": "text",
#             "text": "12 วัน",
#             "size": "xl"
#           }
#         ],
#         "margin": "sm"
#       },
#       {
#         "type": "separator",
#         "margin": "xl"
#       },
#       {
#         "type": "button",
#         "action": {
#           "type": "uri",
#           "label": "รายละเอียดเพิ่มเติม",
#           "uri": "http://pea-covid19-test.herokuapp.com/"
#         },
#         "margin": "xxl"
#       }
#     ],
#     "offsetTop": "-10px"
#   },
#   "size": "mega"
# }
#                                            )
#                                            )
#             elif dict_message['text'] == 'tracking':
#                 pass
#             elif dict_message['text'] == 'timestamp':
#                 line_bot_api.reply_message(event.reply_token,
#                                            FlexSendMessage(
#                                                alt_text='hello',
#                                                contents={
#   "type": "bubble",
#   "body": {
#     "type": "box",
#     "layout": "vertical",
#     "contents": [
#       {
#         "type": "image",
#         "size": "full",
#         "aspectMode": "cover",
#         "gravity": "center",
#         "url": "https://sv1.picz.in.th/images/2020/03/20/QiD33J.png",
#         "aspectRatio": "1:1"
#       },
#       {
#         "type": "image",
#         "url": "https://sv1.picz.in.th/images/2020/03/20/QiAZfS.png",
#         "aspectMode": "cover",
#         "size": "full",
#         "aspectRatio": "1040:174",
#         "action": {
#           "type": "uri",
#           "label": "action",
#           "uri": "https://pea-covid19-test.herokuapp.com/checkin/{}/".format(
#                                                                        user_employee.employee_ID)}
#       }
#     ],
#     "paddingAll": "0px"
#   }
# }
#                                            )
#                                            )
#             elif dict_message['text'] == 'ssss':
#                 line_bot_api.reply_message(event.reply_token,
#                                            FlexSendMessage(
#                                                alt_text='hello',
#                                                contents={
#   "type": "carousel",
#   "contents": [
#     # {
#     #   "type": "bubble",
#     #   "size": "kilo",
#     #   "hero": {
#     #     "type": "image",
#     #     "url": "https://sv1.picz.in.th/images/2020/03/20/QijTae.png",
#     #     "size": "full",
#     #     "aspectMode": "cover",
#     #     "aspectRatio": "320:213"
#     #   },
#     #   "body": {
#     #     "type": "box",
#     #     "layout": "vertical",
#     #     "contents": [
#     #       {
#     #         "type": "text",
#     #         "text": "PEA Support",
#     #         "weight": "bold",
#     #         "size": "xl",
#     #         "wrap": true
#     #       },
#     #       {
#     #         "type": "box",
#     #         "layout": "vertical",
#     #         "contents": [
#     #           {
#     #             "type": "box",
#     #             "layout": "baseline",
#     #             "spacing": "sm",
#     #             "contents": [
#     #               {
#     #                 "type": "text",
#     #                 "text": "คู่มือปฏิบัติตัว COVID-19",
#     #                 "wrap": true,
#     #                 "color": "#8c8c8c",
#     #                 "size": "md",
#     #                 "flex": 5
#     #               }
#     #             ]
#     #           }
#     #         ]
#     #       }
#     #     ],
#     #     "spacing": "sm",
#     #     "paddingAll": "13px"
#     #   },
#     #   "footer": {
#     #     "type": "box",
#     #     "layout": "vertical",
#     #     "contents": [
#     #       {
#     #         "type": "button",
#     #         "action": {
#     #           "type": "message",
#     #           "label": "อ่านเลย",
#     #           "text": "guidecovid"
#     #         }
#     #       }
#     #     ]
#     #   }
#     # },
#     # {
#     #   "type": "bubble",
#     #   "size": "kilo",
#     #   "hero": {
#     #     "type": "image",
#     #     "url": "https://sv1.picz.in.th/images/2020/03/20/QijcdE.png",
#     #     "size": "full",
#     #     "aspectMode": "cover",
#     #     "aspectRatio": "320:213"
#     #   },
#     #   "body": {
#     #     "type": "box",
#     #     "layout": "vertical",
#     #     "contents": [
#     #       {
#     #         "type": "text",
#     #         "text": "วิธีการใช้งาน",
#     #         "weight": "bold",
#     #         "size": "xl",
#     #         "wrap": true
#     #       },
#     #       {
#     #         "type": "box",
#     #         "layout": "vertical",
#     #         "contents": [
#     #           {
#     #             "type": "box",
#     #             "layout": "baseline",
#     #             "spacing": "sm",
#     #             "contents": [
#     #               {
#     #                 "type": "text",
#     #                 "text": "PEA COVID-19 LINE Official Account",
#     #                 "wrap": true,
#     #                 "color": "#8c8c8c",
#     #                 "size": "md",
#     #                 "flex": 5
#     #               }
#     #             ]
#     #           }
#     #         ]
#     #       }
#     #     ],
#     #     "spacing": "sm",
#     #     "paddingAll": "13px"
#     #   },
#     #   "footer": {
#     #     "type": "box",
#     #     "layout": "vertical",
#     #     "contents": [
#     #       {
#     #         "type": "button",
#     #         "action": {
#     #           "type": "message",
#     #           "label": "อ่านเลย",
#     #           "text": "guideline"
#     #         }
#     #       }
#     #     ]
#     #   }
#     # },
#     # {
#     #   "type": "bubble",
#     #   "size": "kilo",
#     #   "hero": {
#     #     "type": "image",
#     #     "url": "https://sv1.picz.in.th/images/2020/03/20/Qijv9I.png",
#     #     "size": "full",
#     #     "aspectMode": "cover",
#     #     "aspectRatio": "320:213"
#     #   },
#     #   "body": {
#     #     "type": "box",
#     #     "layout": "vertical",
#     #     "contents": [
#     #       {
#     #         "type": "text",
#     #         "text": "สายด่วน PEA",
#     #         "weight": "bold",
#     #         "size": "xl",
#     #         "wrap": true
#     #       },
#     #       {
#     #         "type": "box",
#     #         "layout": "vertical",
#     #         "contents": [
#     #           {
#     #             "type": "box",
#     #             "layout": "baseline",
#     #             "spacing": "sm",
#     #             "contents": [
#     #               {
#     #                 "type": "text",
#     #                 "text": "ติดต่อฉุกเฉิน โทร",
#     #                 "wrap": true,
#     #                 "color": "#8c8c8c",
#     #                 "size": "md",
#     #                 "flex": 5
#     #               }
#     #             ]
#     #           }
#     #         ]
#     #       }
#     #     ],
#     #     "spacing": "sm",
#     #     "paddingAll": "13px"
#     #   },
#     #   "footer": {
#     #     "type": "box",
#     #     "layout": "vertical",
#     #     "contents": [
#     #       {
#     #         "type": "button",
#     #         "action": {
#     #           "type": "uri",
#     #           "label": "ติดต่อฉุกเฉิน",
#     #           "uri": "tel:1129"
#     #         }
#     #       }
#     #     ]
#     #   }
#     # },
#     {
#       "type": "bubble",
#       "size": "kilo",
#       "hero": {
#         "type": "image",
#         "url": "https://sv1.picz.in.th/images/2020/03/20/Qil2IN.png",
#         "size": "full",
#         "aspectMode": "cover",
#         "aspectRatio": "320:213"
#       },
#       "body": {
#         "type": "box",
#         "layout": "vertical",
#         "contents": [
#           {
#             "type": "text",
#             "text": "กรมควบคุมโรค",
#             "weight": "bold",
#             "size": "xl",
#             "wrap": true
#           },
#           {
#             "type": "box",
#             "layout": "vertical",
#             "contents": [
#               {
#                 "type": "box",
#                 "layout": "baseline",
#                 "spacing": "sm",
#                 "contents": [
#                   {
#                     "type": "text",
#                     "text": "สายด่วน 1442",
#                     "wrap": true,
#                     "color": "#8c8c8c",
#                     "size": "md",
#                     "flex": 5
#                   }
#                 ]
#               }
#             ]
#           }
#         ],
#         "spacing": "sm",
#         "paddingAll": "13px"
#       },
#       "footer": {
#         "type": "box",
#         "layout": "vertical",
#         "contents": [
#           {
#             "type": "button",
#             "action": {
#               "type": "uri",
#               "label": "ติดต่อฉุกเฉิน",
#               "uri": "tel:1442"
#             }
#           }
#         ]
#       }
#     }
#   ]
# }
#                                            )
#                                            )
#             else:
#                 line_bot_api.reply_message(event.reply_token,
#                                            TextSendMessage(
#                                                text='ส่ง feedback ให้ admin ที่ www.menti.com กรอกรหัส 456368'))
#         except:
#             line_bot_api.reply_message(event.reply_token,
#                                        TextSendMessage(text='ไลน์ไอดีนี้ยังไม่ได้ลงทะเบียน โปรดกรอกรหัสพนักงาน 6 ตัว'))
#
#             # obj = [{'type': 'register', 'datetime': datetime.now().strftime("%Y-%m-%d (%H:%M:%S)")}]
#             # new_user = employee(emplyee_name='blank', employee_line_ID=dict_source['user_id'],
#             #                     employee_ID=dict_message['text'], activity_text=json.dumps(obj), quarantined=False,
#             #                     infected=False)
#             # new_user.save()
#             # line_bot_api.reply_message(event.reply_token,
#             #                            TextSendMessage(text='ระบบได้ลงทะเบียนรหัสพนักงานสำเร็จ '
#             #                                                 'กรุณากรอกแบบฟอร์มคัดกรอง www.https://pea-covid19-test.herokuapp.com/screen/{}/'.format(
#             #                                new_user.employee_ID)))
#
#             # ส่งคำถามคัดกรอง
#
# # push message for question quarantile person
# def send_question():
#     to = 'Ud5a85712fadd31a77c26f24b0e73b74d'
#     line_bot_api.push_message(to, TextSendMessage(text='Hello World!'))

def connect(server, email, username, password):
    """
    Get Exchange account cconnection with server
    """
    creds = Credentials(username=username, password=password)
    config = Configuration(server=server, credentials=creds)
    return Account(primary_smtp_address=email, autodiscover=False, config=config, access_type=DELEGATE)


def print_tree(account):
    """
    Print folder tree
    """
    print(account.root.tree())

def get_recent_emails(account, folder_name, count):
    """
    Retrieve most emails for a given folder
    """
    # Get the folder object
    folder = account.root / 'Top of Information Store' / folder_name
    # Get emails
    return folder.all().order_by('-datetime_received')[:count]

def count_senders(emails):
    """
    Given emails, provide counts of sender by name
    """
    counts = defaultdict(int)
    for email in emails:
        counts[email.sender.name] += 1
    return counts

def print_non_replies(emails, agents):
    """
    Print subjects where no agents have replied
    """
    dealt_with = dict()
    not_dealt_with = dict()
    not_dealt_with_list = list()
    for email in emails:  # newest to oldest
        # Simplify subject
        subject = email.subject.lower().replace('re: ', '').replace('fw: ', '')

        if subject in dealt_with or subject in not_dealt_with:
            continue
        elif email.sender.name in agents:
            # If most recent email was from an agent it's been dealt with
            dealt_with[subject] = email
        else:
            # Email from anyone else has not been dealt with
            not_dealt_with[subject] = email
            not_dealt_with_list += [email.subject]

    print('NOT DEALT WITH:')
    for subject in not_dealt_with_list:
        print(' * ', subject)


# def get_user_data(id):
#     with open('idm.json') as f:
#         dict_data = json.load(f)
#     return dict_data[id]['email']


def get_user_email(id):
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
    authData = jsonconvert["soap:Envelope"]['soap:Body']['GetEmployeeInfoByEmployeeId_SIResponse'][
        'GetEmployeeInfoByEmployeeId_SIResult']['ResultObject']

    return authData.get("Email")

#### สมัคร
def send_email_register(email, line_id, id):
    recipient_list = [email]
    print('receipient list', recipient_list)
    # subject = 'ยืนยันการสมัคร'
    # message = ' กดที่ link  https://pea-covid19-test.herokuapp.com/confirm_registration/{}{}'.format(line_id, id)
    server = 'email.pea.co.th'
    email = 'chakkrit.ben@pea.co.th'
    username = '507192'
    password = 'l2eleaser+'
    account = connect(server, email, username, password)
    subject = 'ยืนยันการสมัคร'
    body = ' กดที่ link  https://pea-covid19-test.herokuapp.com/register/{}{}'.format(line_id, id)
    m = Message(account=account,
                subject=subject,
                body=body,
                to_recipients=recipient_list)
    print('message created')
    m.send_and_save()
    print(m)
    print('email send')


    # email_from = settings.EMAIL_HOST_USER
    # send_mail(subject, message, email_from, recipient_list)


def register(request, id):
    # data = employee.objects.get(employee_ID=id).__dict__

    emp_id = id[33:]
    line_id = id[0:33]

    try:
        employee.objects.get(employee_line_ID=line_id)
        return redirect(home)
    except:
        pass

    context = {'data': {'id': emp_id}}

    emp_id = ''
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
        page = request.POST.get("page")
        print(page)
        if (page == "1"):
            print("OK1")
            emp_id = request.POST.get("emp_id")
            sex = request.POST.get("sex")
            age = request.POST.get("age")
            tel = request.POST.get("tel")
            work_place = request.POST.get("work_place")
            work_building = request.POST.get("work_building")
            work_floor = request.POST.get("work_floor")

            return render(request, 'myworkplace/register_2.html', context)

        if (page == "2"):
            print("OK2")
            address_no = request.POST.get("address_no")
            address_tumbol = request.POST.get("address_tumbol")
            address_amphur = request.POST.get("address_amphur")
            address_province = request.POST.get("address_province")
            address_type = request.POST.get("address_type")
            address_to_live = request.POST.get("address_to_live")
            detention_place = request.POST.get("detention_place")

            return render(request, 'myworkplace/register_3.html', context)

        if (page == "3"):
            print("OK3")
            blood = request.POST.get("blood")
            congenital_disease_status = request.POST.get("congenital_disease_status")
            congenital_disease = request.POST.get("congenital_disease")
            drug_allergy_history_status = request.POST.get("drug_allergy_history_status")
            drug_allergy_history = request.POST.get("drug_allergy_history")
            respiratory_disease_status = request.POST.get("respiratory_disease_status")
            respiratory_disease = request.POST.get("respiratory_disease")
            last_disease = request.POST.get("last_disease")
            last_hospital = request.POST.get("last_hospital")
            last_time_status = request.POST.get("last_time_status")
            favorite_hospital = request.POST.get("favorite_hospital")

            return render(request, 'myworkplace/register_4.html', context)

        if (page == "4"):
            print("OK4")
            close_person_first_name = request.POST.get("close_person_first_name")
            close_person_last_name = request.POST.get("close_person_last_name")
            close_person_tel = request.POST.get("close_person_tel")
            close_person_relationship = request.POST.get("close_person_relationship")
            workmate_first_name = request.POST.get("workmate_first_name")
            workmate_last_name = request.POST.get("workmate_last_name")
            workmate_tel = request.POST.get("workmate_tel")
            emergency_one_first_name = request.POST.get("emergency_one_first_name")
            emergency_one_last_name = request.POST.get("emergency_one_last_name")
            emergency_one_tel = request.POST.get("emergency_one_tel")
            emergency_two_first_name = request.POST.get("emergency_two_first_name")
            emergency_two_last_name = request.POST.get("emergency_two_last_name")
            emergency_two_tel = request.POST.get("emergency_two_tel")

            obj = {'type': 'register', 'datetime': datetime.now().strftime("%Y-%m-%d (%H:%M:%S)")}

            print(emp_id)

            user_data = employee(
                employee_ID=emp_id,
                employee_line_ID=line_id,
                activity_text=json.dumps([obj], ensure_ascii=False),
                sex=sex,
                age=age,
                tel=tel,
                work_place=work_place,
                work_building=work_building,
                work_floor=work_floor,

                address_no=address_no,
                address_tumbol=address_tumbol,
                address_amphur=address_amphur,
                address_province=address_province,
                address_type=address_type,
                address_to_live=address_to_live,
                detention_place=detention_place,

                blood=blood,
                congenital_disease_status=congenital_disease_status,
                congenital_disease=congenital_disease,
                drug_allergy_history_status=drug_allergy_history_status,
                drug_allergy_history=drug_allergy_history,
                respiratory_disease_status=respiratory_disease_status,
                respiratory_disease=respiratory_disease,
                last_disease=last_disease,
                last_hospital=last_hospital,
                last_time_status=last_time_status,
                favorite_hospital=favorite_hospital,

                close_person_first_name=close_person_first_name,
                close_person_last_name=close_person_last_name,
                close_person_tel=close_person_tel,
                close_person_relationship=close_person_relationship,
                workmate_first_name=workmate_first_name,
                workmate_last_name=workmate_last_name,
                workmate_tel=workmate_tel,
                emergency_one_first_name=emergency_one_first_name,
                emergency_one_last_name=emergency_one_last_name,
                emergency_one_tel=emergency_one_tel,
                emergency_two_first_name=emergency_two_first_name,
                emergency_two_last_name=emergency_two_last_name,
                emergency_two_tel=emergency_two_tel
            )

            user_data.save()

            return render(request, 'myworkplace/register_finish.html', context)

    return render(request, 'myworkplace/register_1.html', context)


def confirm_registration(request, id):
    employee_id = id[33:]
    employee_line_id = id[0:33]
    try:
        employee.objects.get(employee_line_ID=employee_line_id)
        print('ท่านได้ลงทะเบียนซ้ำซ้อนน')
        return render(request, 'myworkplace/home.html')
    except:
        print('start saving user')
        obj = [{'type': 'register', 'datetime': datetime.now().strftime("%Y-%m-%d (%H:%M:%S)")}]
        new_user = employee(employee_line_ID=employee_line_id, employee_ID=employee_id, activity_text=json.dumps(obj))
        new_user.save()
        print('ลงทะเบียนใหม่')
        return render(request, 'myworkplace/home.html')

######## challenge

def randomquestions(request, id):
    ranquestions = question.objects.get(pk=random.randint(0, len(question.objects.all()) - 1))

    context = {'data': ranquestions}
    user = employee.objects.get(employee_ID=str(id))

    if request.method == "POST":
        answer = request.POST.get("exampleRadios")
        correct = request.POST.get("correct")
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")
        obj = {'type': 'question', 'answer':answer==correct, 'latitude': latitude, 'longitude': longitude,
               'datetime': datetime.now().strftime("%Y-%m-%d (%H:%M:%S)")}
        data = json.loads(user.activity_text)
        data.append(obj)
        user.activity_text = json.dumps(data, ensure_ascii=False)
        user.save()
        if (answer == correct):
            return render(request, 'myworkplace/correct.html')
        else:
            return render(request, 'myworkplace/wrong.html')

    return render(request, 'myworkplace/challenge2.html', context)


# def challenge(request, id):
#     data = employee.objects.get(employee_ID=id).__dict__
#     context = {'data': data}
#
#     if request.method == "POST":
#         latitude = request.POST.get("latitude")
#         longitude = request.POST.get("longitude")
#         print('##########-----------##########')
#         print('latitute is', latitude)
#         obj = {'type': 'question', 'latitude': latitude, 'longitude': longitude,
#                'datetime': datetime.now().strftime("%Y-%m-%d (%H:%M:%S)")}
#
#         user = employee.objects.get(employee_ID=id)
#         data = json.loads(user.activity_text)
#         data.append(obj)
#         print(data)
#         user.activity_text = json.dumps(data, ensure_ascii=False)
#         user.save()
#         context['data'].update({'datetime': obj['datetime']})
#         return render(request, 'myworkplace/checkinComplete.html', context)
#
#     return render(request, 'myworkplace/challenge.html', context)


def wrong(request):
    return render(request, 'myworkplace/wrong.html')

def correct(request):
    return render(request, 'myworkplace/correct.html')


def miss3d_du(request, id):
    data = employee.objects.get(employee_ID=str(id)).__dict__
    context = {'data': data}

    return render(request, 'myworkplace/miss3d_du_id.html', context)


def miss3d_ts(request, id):
    data = employee.objects.get(employee_ID=str(id)).__dict__
    context = {'data': data, 'number':40}

    return render(request, 'myworkplace/miss3d_ts_id.html', context)


###### sent email #########

def connect(server, email, username, password):
    """
    Get Exchange account cconnection with server
    """
    creds = Credentials(username=username, password=password)
    config = Configuration(server=server, credentials=creds)
    return Account(primary_smtp_address=email, autodiscover=False, config=config, access_type=DELEGATE)


def print_tree(account):
    """
    Print folder tree
    """
    print(account.root.tree())


def get_recent_emails(account, folder_name, count):
    """
    Retrieve most emails for a given folder
    """
    # Get the folder object
    folder = account.root / 'Top of Information Store' / folder_name
    # Get emails
    return folder.all().order_by('-datetime_received')[:count]


def count_senders(emails):
    """
    Given emails, provide counts of sender by name
    """
    counts = defaultdict(int)
    for email in emails:
        counts[email.sender.name] += 1
    return counts


def print_non_replies(emails, agents):
    """
    Print subjects where no agents have replied
    """
    dealt_with = dict()
    not_dealt_with = dict()
    not_dealt_with_list = list()
    for email in emails:  # newest to oldest
        # Simplify subject
        subject = email.subject.lower().replace('re: ', '').replace('fw: ', '')

        if subject in dealt_with or subject in not_dealt_with:
            continue
        elif email.sender.name in agents:
            # If most recent email was from an agent it's been dealt with
            dealt_with[subject] = email
        else:
            # Email from anyone else has not been dealt with
            not_dealt_with[subject] = email
            not_dealt_with_list += [email.subject]

    print('NOT DEALT WITH:')
    for subject in not_dealt_with_list:
        print(' * ', subject)


def send_email(request, id, case, boss, day):
    server = 'email.pea.co.th'
    email = 'chakkrit.ben@pea.co.th'
    username = '507192'
    password = 'l2eleaser+'
    account = connect(server, email, username, password)
    if case == 'Leave_COVID_19':
        subject = 'พนักงานของท่านขอลาเนื่องจากติดเชื้อ COVID-19'
        body = 'สวัสดี พนักงานรหัส {} ขอลาเนื่องจากติดโควิด'.format(id)
    elif case == 'Leave_WFH_2':
        subject = 'พนักงานของท่านขอลา WFH แบบที่ 2'
        body = 'สวัสดี พนักงานรหัส {} ขอลา WFH แบบที่ 2 เป็นเวลา {} หากอนุมัติให้กด http://127.0.0.1:8000/confirm_leave_WFH_2/{}/{}'.format(
            id, day, id, boss)
    elif case == 'Leave_WFH_1':
        subject = 'พนักงานของท่านขอลา WFH แบบที่ 1'
        body = 'สวัสดี พนักงานรหัส {} ขอลา WFH แบบที่ 1 ให้ลาได้ {} วัน หากอนุมัติให้กด http://127.0.0.1:8000/confirm_leave_WFH_1/{}/{}/{}'.format(
            id, day, id, boss, day)
    else:
        pass

    m = Message(account=account,
                subject=subject,
                body=body,
                to_recipients=[boss])
    print('message created')
    m.send_and_save()
    print(m)
    print('email send')

    return render(request, 'myworkplace/confirm_WFH.html')


def send_email_leave_covid(request, id, boss):
    server = 'email.pea.co.th'
    email = 'chakkrit.ben@pea.co.th'
    username = '507192'
    password = 'l2eleaser+'
    account = connect(server, email, username, password)
    boss = boss + '@pea.co.th'

    subject = 'พนักงานของท่านขอลาเนื่องจากติดเชื้อ COVID-19'
    body = 'สวัสดี พนักงานรหัส {} ขอลาเนื่องจากติดโควิด'.format(id)
    m = Message(account=account,
                subject=subject,
                body=body,
                to_recipients=[boss])
    print('message created')
    m.send_and_save()
    print(m)
    print('email send')

    return render(request, 'myworkplace/confirm_WFH.html')


def send_email_leave_wfh_2(request, id, boss):
    server = 'email.pea.co.th'
    email = 'chakkrit.ben@pea.co.th'
    username = '507192'
    password = 'l2eleaser+'
    account = connect(server, email, username, password)
    boss = boss + '@pea.co.th'
    subject = 'พนักงานของท่านขอลา WFH แบบที่ 2'
    body = 'สวัสดี พนักงานรหัส {} ขอลา WFH แบบที่ 2 เป็นเวลา 14 หากอนุมัติให้กด http://127.0.0.1:8000/confirm_leave_WFH_2/{}/{}'.format(
        id, id, boss)
    m = Message(account=account,
                subject=subject,
                body=body,
                to_recipients=[boss])
    print('message created')
    m.send_and_save()
    print(m)
    print('email send')
    return render(request, 'myworkplace/confirm_WFH.html')


def send_email_leave_wfh_1(request, id, boss, day):
    server = 'email.pea.co.th'
    email = 'chakkrit.ben@pea.co.th'
    username = '507192'
    password = 'l2eleaser+'
    boss = boss + '@pea.co.th'
    account = connect(server, email, username, password)
    subject = 'พนักงานของท่านขอลา WFH แบบที่ 1'
    body = 'สวัสดี พนักงานรหัส {} ขอลา WFH แบบที่ 1 ให้ลาได้ {} วัน หากอนุมัติให้กด http://127.0.0.1:8000/confirm_leave_WFH_1/{}/{}/{}'.format(
        id, day, id, boss, day)
    m = Message(account=account,
                subject=subject,
                body=body,
                to_recipients=[boss])
    print('message created')
    m.send_and_save()
    print(m)
    print('email send')

    return render(request, 'myworkplace/confirm_WFH.html')


def confirm_leave_WFH_2(request, id, boss):
    obj = {'type': 'leave_WFH_2', 'approved_by': boss,
           'start_date': (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
           'finish_date': (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d"),
           'datetime': datetime.now().strftime("%Y-%m-%d (%H:%M:%S)")}

    user = employee.objects.get(employee_ID=str(id))
    print(user)
    data = json.loads(user.activity_text)
    data.append(obj)
    user.activity_text = json.dumps(data, ensure_ascii=False)
    user.save()
    return render(request, 'myworkplace/confirm_WFH.html')

def confirm_leave_WFH_1(request, id, boss, day):
    obj = {'type': 'leave_WFH_1', 'approved_by': boss,
           'start_date': (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
           'finish_date': (datetime.now() + timedelta(days=int(day))).strftime("%Y-%m-%d"),
           'datetime': datetime.now().strftime("%Y-%m-%d (%H:%M:%S)")}

    user = employee.objects.get(employee_ID=str(id))
    print(user)
    data = json.loads(user.activity_text)
    data.append(obj)
    user.activity_text = json.dumps(data, ensure_ascii=False)
    user.save()
    return render(request, 'myworkplace/confirm_WFH.html')


