from django.shortcuts import render
from django.db import connection
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from myworkplace.models import employee
from send_email.views import send_email_register, get_user_email
import asyncio

# Create your views here.

from django.http import HttpResponseForbidden, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (
    MessageEvent,
    TextMessage,
    TextSendMessage,
    FlexSendMessage,
    ImageSendMessage,
)

import os

# YOUR_CHANNEL_ACCESS_TOKEN = os.environ["Ga+IdjcgPa032XLB5IaBPG2Fk+1VLs1+Lc+KFmbSjJXLZK+9RTT3+oyxqd9dG0dejJQ0a8LHz8dk8uXj6WJ/XjXpZzWRz9qRYyQNiOXwPbi7qa16vCYm1UwgL5mHF3j/Rk7ca5oxnKshQIyUizbQlwdB04t89/1O/w1cDnyilFU="]
# YOUR_CHANNEL_SECRET = os.environ["ada0193e1d7e79a4aa93a938b9300246"]

YOUR_CHANNEL_ACCESS_TOKEN = "O9WalOm/R+TB7PdDOli1Bg20ZTEIWL4VdoDQFHbRPP2TWafBO/Xf+V7lq2oT/7AsRX+ILQK6FwcU6r+e69Ca/b0veDKZc0mp9cw+/Y4pkAWL9Wu8sX6Ospg4jzzs0Wwpdt27QjN9KjdjDoE8ljgn5AdB04t89/1O/w1cDnyilFU="

YOUR_CHANNEL_SECRET = "3159d75a7c0f34bf72a9609987675644"

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
    # print(body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        HttpResponseForbidden()
    return HttpResponse('OK', status=200)


# # オウム返し
@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    print('Here is handle_text_message function')
    dict_event = event.__dict__
    # print(dict_event)
    dict_source = dict_event['source'].__dict__
    dict_message = dict_event['message'].__dict__
    # print(dict_message['text'])
    # line_bot_api.reply_message(event.reply_token,
    #                            # TextSendMessage(text='ไลน์ไอดีนี้ยังไม่ได้ลงทะเบียน โปรดกรอกรหัสพนักงาน 6 ตัว'))
    #                            TextSendMessage(
    #                                text='ตอนนี้ระบบปิดทำการชั่วคราวเพื่อปรับปรุงคร่าาา จะกลับมาอีกทีเร็วๆนี้'))
    if dict_message['text'].isnumeric() and (
            len(dict_message['text']) == 6 or len(dict_message['text']) == 7):
        ##### function create email กับ content ข้างใน
        try:
            user_employee = employee.objects.get(employee_line_ID=dict_source['user_id'])
            connection.close()
            line_bot_api.reply_message(event.reply_token,
                                       TextSendMessage(text='ท่านได้ลงทะเบียนแล้ว'))
        except ObjectDoesNotExist:
            first_name, last_name, sex_desc, posi_text_short, dept_sap_short, dept_sap, dept_upper, sub_region, emp_email = get_user_email(
                id=dict_message['text'])
            if emp_email is not None:
                # line_bot_api.reply_message(event.reply_token,
                #                            TextSendMessage(text='ขณะนี้เรากำลังปรับปรุงระบบลงทะเบียนเพื่อรองรับผู้ใช้งานจำนวนมาก กรุณาลงทะเบียนอีกครั้งภายหลัง'))
                # print('{} no email in system'.format(dict_message['text']))
                try:
                    send_email_register(emp_email=emp_email, line_id=dict_source['user_id'], id=dict_message['text'])
                    line_bot_api.reply_message(event.reply_token,
                                               TextSendMessage(
                                                   text='โปรดทำการยืนยันตัวตนของคุณผ่าน PEA Mail เพื่อเข้าสู่ระบบตาม link ด้านล่างนี้ https://email.pea.co.th '
                                                        '(username คือรหัสพนักงาน 6 หลัก)'),
                                               )
                except:
                    line_bot_api.reply_message(event.reply_token,
                                               TextSendMessage(text='ลองอีกครั้ง'))
                    print('{} no email in system'.format(dict_message['text']))
            else:
                line_bot_api.reply_message(event.reply_token,
                                           [TextSendMessage(
                                               text='ไปกรอกอีเมล์ใน IDM ด้วย http://idm.pea.co.th'),
                                               ImageSendMessage(
                                                   original_content_url='https://www.img.in.th/images/600a10b547eb587a9d42525edcce704f.jpg',
                                                   preview_image_url='https://www.img.in.th/images/600a10b547eb587a9d42525edcce704f.jpg'
                                               ),
                                               ImageSendMessage(
                                                   original_content_url='https://www.img.in.th/images/7ba36f03f09d94f2a8a692297e364db2.jpg',
                                                   preview_image_url='https://www.img.in.th/images/7ba36f03f09d94f2a8a692297e364db2.jpg'
                                               ),
                                               ImageSendMessage(
                                                   original_content_url='https://www.imag.in.th/images/031525e6dce37aa260bac21483c11522.jpg',
                                                   preview_image_url='https://www.imag.in.th/images/031525e6dce37aa260bac21483c11522.jpg'
                                               )
                                           ])

        except MultipleObjectsReturned:
            line_bot_api.reply_message(event.reply_token,
                                       TextSendMessage(text='ไลน์ไอดีนี้มีมากกว่า 2 บัญชี โปรดแจ้ง admin'))
    else:
        try:
            user_employee = employee.objects.get(employee_line_ID=dict_source['user_id'])
            connection.close()
            if dict_message['text'] == 'ขออนุมัติ':
                line_bot_api.reply_message(event.reply_token,
                                           FlexSendMessage(
                                               alt_text='hello',
                                               contents={
                                                   "type": "carousel",
                                                   "contents": [
                                                       {
                                                           "type": "bubble",
                                                           "body": {
                                                               "type": "box",
                                                               "layout": "vertical",
                                                               "contents": [
                                                                   {
                                                                       "type": "image",
                                                                       "size": "full",
                                                                       "aspectMode": "cover",
                                                                       "gravity": "center",
                                                                       "aspectRatio": "1:1",
                                                                       "url": "https://sv1.picz.in.th/images/2020/03/19/Qi9EIN.png"
                                                                   },
                                                                   {
                                                                       "type": "image",
                                                                       "url": "https://www.img9.in.th/images/2020/03/19/-WFHb1.png",
                                                                       "aspectMode": "cover",
                                                                       "size": "full",
                                                                       "action": {
                                                                           "type": "uri",
                                                                           "label": "action",
                                                                           "uri": "https://pea-covid19-test.herokuapp.com/formwfh1/{}/".format(
                                                                               user_employee.employee_ID)
                                                                       },
                                                                       "aspectRatio": "1040:174"
                                                                   }
                                                               ],
                                                               "paddingAll": "0px"
                                                           }
                                                       },
                                                       {
                                                           "type": "bubble",
                                                           "body": {
                                                               "type": "box",
                                                               "layout": "vertical",
                                                               "contents": [
                                                                   {
                                                                       "type": "image",
                                                                       "size": "full",
                                                                       "aspectMode": "cover",
                                                                       "gravity": "center",
                                                                       "url": "https://sv1.picz.in.th/images/2020/03/19/Qi9wFu.png",
                                                                       "aspectRatio": "1:1"
                                                                   },
                                                                   {
                                                                       "type": "image",
                                                                       "url": "https://sv1.picz.in.th/images/2020/03/19/Qi9Rqe.png",
                                                                       "aspectMode": "cover",
                                                                       "size": "full",
                                                                       "aspectRatio": "1040:174",
                                                                       "action": {
                                                                           "type": "uri",
                                                                           "label": "action",
                                                                           "uri": "https://pea-covid19-test.herokuapp.com/meet_doc2/{}/".format(
                                                                               user_employee.employee_ID)
                                                                       }
                                                                   }
                                                               ],
                                                               "paddingAll": "0px"
                                                           }
                                                       }
                                                   ]
                                               }
                                           )
                                           )
            elif dict_message['text'] == 'test':
                # print('ทดสอบ ส่งอีเมล')
                line_bot_api.reply_message(event.reply_token,
                                           TextSendMessage(text='ทดสอบ'))
            elif dict_message['text'] == 'ประเมินความเสี่ยง':
                line_bot_api.reply_message(event.reply_token,
                                           FlexSendMessage(
                                               alt_text='hello',
                                               contents={
                                                   "type": "carousel",
                                                   "contents": [
                                                       {
                                                           "type": "bubble",
                                                           "body": {
                                                               "type": "box",
                                                               "layout": "vertical",
                                                               "contents": [
                                                                   {
                                                                       "type": "image",
                                                                       "size": "full",
                                                                       "aspectMode": "cover",
                                                                       "gravity": "center",
                                                                       "url": "https://s3-ap-southeast-1.amazonaws.com/img-in-th/c4ab0fa44c5e576502ec90d88b2bbbe5.png",
                                                                       "aspectRatio": "1:1"
                                                                   },
                                                                   {
                                                                       "type": "image",
                                                                       "url": "https://sv1.picz.in.th/images/2020/03/19/QgvxrE.png",
                                                                       "aspectMode": "cover",
                                                                       "size": "full",
                                                                       "aspectRatio": "1040:174",
                                                                       "action": {
                                                                           "type": "uri",
                                                                           "label": "action",
                                                                           "uri": "https://pea-covid19-test.herokuapp.com/daily_update/{}".format(
                                                                               user_employee.employee_ID)
                                                                       }
                                                                   }
                                                               ],
                                                               "paddingAll": "0px"
                                                           }
                                                       },
                                                       {
                                                           "type": "bubble",
                                                           "body": {
                                                               "type": "box",
                                                               "layout": "vertical",
                                                               "contents": [
                                                                   {
                                                                       "type": "image",
                                                                       "size": "full",
                                                                       "aspectMode": "cover",
                                                                       "gravity": "center",
                                                                       "url": "https://sv1.picz.in.th/images/2020/03/19/QgLwmJ.png",
                                                                       "aspectRatio": "1:1"
                                                                   },
                                                                   {
                                                                       "type": "image",
                                                                       "url": "https://sv1.picz.in.th/images/2020/03/19/QgLts9.png",
                                                                       "aspectMode": "cover",
                                                                       "size": "full",
                                                                       "aspectRatio": "1040:174",
                                                                       "action": {
                                                                           "type": "uri",
                                                                           "label": "action",
                                                                           "uri": "https://pea-covid19-test.herokuapp.com/test/"
                                                                       }
                                                                   }
                                                               ],
                                                               "paddingAll": "0px"
                                                           }
                                                       }
                                                   ]
                                               }

                                           ))
            elif dict_message['text'] == 'ข้อมูลส่วนตัว':
                try:
                    line_bot_api.reply_message(event.reply_token,
                                               TextSendMessage(text='ฟังก์ชั่นนี้อยู่ระหว่างการพัฒนา อดใจรอสักครู่'))
                    # d, t = user_employee.last_daily_update()
                    # line_bot_api.reply_message(event.reply_token,
                    #                            FlexSendMessage(
                    #                                alt_text='hello',
                    #                                contents=
                    #                                # {
                    #                                #     "type": "bubble",
                    #                                #     "hero": {
                    #                                #         "type": "image",
                    #                                #         "url": "https://sv1.picz.in.th/images/2020/03/19/QiOkcu.png",
                    #                                #         "size": "full",
                    #                                #         "action": {
                    #                                #             "type": "uri",
                    #                                #             "uri": "http://linecorp.com/"
                    #                                #         },
                    #                                #         "aspectMode": "cover",
                    #                                #         "aspectRatio": "1040:677"
                    #                                #     },
                    #                                #     "body": {
                    #                                #         "type": "box",
                    #                                #         "layout": "vertical",
                    #                                #         "contents": [
                    #                                #             {
                    #                                #                 "type": "text",
                    #                                #                 "text": "{}".format(user_employee.emplyee_name),
                    #                                #                 "weight": "bold",
                    #                                #                 "size": "xl",
                    #                                #                 "align": "center"
                    #                                #             },
                    #                                #             {
                    #                                #                 "type": "text",
                    #                                #                 "text": "{}".format(user_employee.employee_ID),
                    #                                #                 "align": "center",
                    #                                #                 "size": "xl",
                    #                                #                 "weight": "bold"
                    #                                #             },
                    #                                #             {
                    #                                #                 "type": "box",
                    #                                #                 "layout": "horizontal",
                    #                                #                 "contents": [
                    #                                #                     {
                    #                                #                         "type": "text",
                    #                                #                         "text": "ความเสี่ยง :",
                    #                                #                         "size": "xl"
                    #                                #                     },
                    #                                #                     {
                    #                                #                         "type": "text",
                    #                                #                         "text": "{}".format({'normal': 'ไม่เข้าเกณฑ์',
                    #                                #                                              'flu': 'ไม่เข้าเกณฑ์',
                    #                                #                                              'quarantine': 'แยกตัว',
                    #                                #                                              'hospital': 'ควรพบแพทย์'}[
                    #                                #                                                 user_employee.healthy]),
                    #                                #                         "size": "xl"
                    #                                #                     }
                    #                                #                 ],
                    #                                #                 "margin": "md"
                    #                                #             },
                    #                                #             {
                    #                                #                 "type": "box",
                    #                                #                 "layout": "horizontal",
                    #                                #                 "contents": [
                    #                                #                     {
                    #                                #                         "type": "text",
                    #                                #                         "text": "สถานะ :",
                    #                                #                         "size": "xl"
                    #                                #                     },
                    #                                #                     {
                    #                                #                         "type": "text",
                    #                                #                         "text": "{}".format({'PEA': 'ปฏิบัติงานตามปกติ',
                    #                                #                                              'WFH': 'Work from home',
                    #                                #                                              'LEAVE': 'ลาป่วย',
                    #                                #                                              'COVID': 'COVID'}[
                    #                                #                                                 user_employee.active_status]),
                    #                                #                         "size": "xl"
                    #                                #                     }
                    #                                #                 ],
                    #                                #                 "margin": "sm"
                    #                                #             },
                    #                                #             {
                    #                                #                 "type": "box",
                    #                                #                 "layout": "horizontal",
                    #                                #                 "contents": [
                    #                                #                     {
                    #                                #                         "type": "text",
                    #                                #                         "text": "วันที่ประเมิน :",
                    #                                #                         "size": "xl"
                    #                                #                     },
                    #                                #                     {
                    #                                #                         "type": "text",
                    #                                #                         "text": "{}".format(d),
                    #                                #                         "size": "xl"
                    #                                #                     }
                    #                                #                 ],
                    #                                #                 "margin": "sm"
                    #                                #             },
                    #                                #             {
                    #                                #                 "type": "box",
                    #                                #                 "layout": "horizontal",
                    #                                #                 "contents": [
                    #                                #                     {
                    #                                #                         "type": "text",
                    #                                #                         "text": "เวลา",
                    #                                #                         "size": "xl",
                    #                                #                         "align": "start"
                    #                                #                     },
                    #                                #                     {
                    #                                #                         "type": "text",
                    #                                #                         "text": "{} น.".format(t),
                    #                                #                         "size": "xl"
                    #                                #                     }
                    #                                #                 ],
                    #                                #                 "margin": "sm"
                    #                                #             },
                    #                                #             # {
                    #                                #             #     "type": "box",
                    #                                #             #     "layout": "horizontal",
                    #                                #             #     "contents": [
                    #                                #             #         {
                    #                                #             #             "type": "text",
                    #                                #             #             "text": "เหลือเวลา",
                    #                                #             #             "size": "xl"
                    #                                #             #         },
                    #                                #             #         {
                    #                                #             #             "type": "text",
                    #                                #             #             "text": "12 วัน",
                    #                                #             #             "size": "xl"
                    #                                #             #         }
                    #                                #             #     ],
                    #                                #             #     "margin": "sm"
                    #                                #             # },
                    #                                #             {
                    #                                #                 "type": "separator",
                    #                                #                 "margin": "xl"
                    #                                #             },
                    #                                #             {
                    #                                #                 "type": "button",
                    #                                #                 "action": {
                    #                                #                     "type": "uri",
                    #                                #                     "label": "รายละเอียดเพิ่มเติม",
                    #                                #                     "uri": "http://pea-covid19-test.herokuapp.com/test/"
                    #                                #                 },
                    #                                #                 "margin": "xxl"
                    #                                #             }
                    #                                #         ],
                    #                                #         "offsetTop": "-10px"
                    #                                #     },
                    #                                #     "size": "mega"
                    #                                # }
                    #
                    # {
                    #     "type": "bubble",
                    #     "size": "giga",
                    #     "body": {
                    #         "type": "box",
                    #         "layout": "vertical",
                    #         "contents": [
                    #             {
                    #                 "type": "text",
                    #                 "text": "ข้อมูลส่วนตัว (My Profile)",
                    #                 "weight": "bold",
                    #                 "color": "#8448FF",
                    #                 "size": "md"
                    #             },
                    #             {
                    #                 "type": "text",
                    #                 "text": "อรรถพล วัฒนสาครกุล",
                    #                 "weight": "bold",
                    #                 "size": "xxl",
                    #                 "margin": "md"
                    #             },
                    #             {
                    #                 "type": "text",
                    #                 "text": "ผวจ. กวจ. ฝวพ.",
                    #                 "size": "sm",
                    #                 "color": "#aaaaaa"
                    #             },
                    #             {
                    #                 "type": "separator",
                    #                 "margin": "xxl"
                    #             },
                    #             {
                    #                 "type": "box",
                    #                 "layout": "horizontal",
                    #                 "contents": [
                    #                     {
                    #                         "type": "text",
                    #                         "text": "ความเสี่ยง",
                    #                         "size": "md",
                    #                         "color": "#111111",
                    #                         "flex": 0
                    #                     },
                    #                     {
                    #                         "type": "text",
                    #                         "text": "แยกตัวเอง",
                    #                         "color": "#111111",
                    #                         "size": "md",
                    #                         "align": "end",
                    #                         "weight": "bold"
                    #                     }
                    #                 ],
                    #                 "margin": "md"
                    #             },
                    #             {
                    #                 "type": "box",
                    #                 "layout": "horizontal",
                    #                 "contents": [
                    #                     {
                    #                         "type": "text",
                    #                         "text": "ประเมินล่าสุด",
                    #                         "size": "md",
                    #                         "color": "#aaaaaa",
                    #                         "flex": 0
                    #                     },
                    #                     {
                    #                         "type": "text",
                    #                         "text": "12/04/2020",
                    #                         "color": "#111111",
                    #                         "size": "md",
                    #                         "align": "end",
                    #                         "weight": "regular"
                    #                     }
                    #                 ]
                    #             },
                    #             {
                    #                 "type": "box",
                    #                 "layout": "horizontal",
                    #                 "contents": [
                    #                     {
                    #                         "type": "text",
                    #                         "text": "เวลา",
                    #                         "size": "md",
                    #                         "color": "#aaaaaa"
                    #                     },
                    #                     {
                    #                         "type": "text",
                    #                         "text": "06:20:45",
                    #                         "size": "md",
                    #                         "color": "#111111",
                    #                         "align": "end"
                    #                     }
                    #                 ]
                    #             },
                    #             {
                    #                 "type": "separator",
                    #                 "margin": "xxl"
                    #             },
                    #             {
                    #                 "type": "box",
                    #                 "layout": "horizontal",
                    #                 "margin": "md",
                    #                 "contents": [
                    #                     {
                    #                         "type": "text",
                    #                         "text": "สถานะ",
                    #                         "size": "md",
                    #                         "color": "#111111",
                    #                         "flex": 0
                    #                     },
                    #                     {
                    #                         "type": "text",
                    #                         "text": "Work from Home",
                    #                         "color": "#111111",
                    #                         "size": "md",
                    #                         "align": "end",
                    #                         "weight": "bold"
                    #                     }
                    #                 ]
                    #             },
                    #             {
                    #                 "type": "box",
                    #                 "layout": "vertical",
                    #                 "margin": "md",
                    #                 "spacing": "sm",
                    #                 "contents": [
                    #                     {
                    #                         "type": "box",
                    #                         "layout": "horizontal",
                    #                         "contents": [
                    #                             {
                    #                                 "type": "text",
                    #                                 "text": "วันเริ่มต้น",
                    #                                 "size": "md",
                    #                                 "color": "#aaaaaa"
                    #                             },
                    #                             {
                    #                                 "type": "text",
                    #                                 "text": "27/03/2020",
                    #                                 "size": "md",
                    #                                 "color": "#111111",
                    #                                 "align": "end"
                    #                             }
                    #                         ]
                    #                     },
                    #                     {
                    #                         "type": "box",
                    #                         "layout": "horizontal",
                    #                         "contents": [
                    #                             {
                    #                                 "type": "text",
                    #                                 "text": "วันที่สิ้นสุด",
                    #                                 "size": "md",
                    #                                 "color": "#aaaaaa"
                    #                             },
                    #                             {
                    #                                 "type": "text",
                    #                                 "text": "12/04/2020",
                    #                                 "size": "md",
                    #                                 "color": "#111111",
                    #                                 "align": "end"
                    #                             }
                    #                         ]
                    #                     },
                    #                     {
                    #                         "type": "box",
                    #                         "layout": "horizontal",
                    #                         "contents": [
                    #                             {
                    #                                 "type": "text",
                    #                                 "text": "รวม (วัน)",
                    #                                 "size": "md",
                    #                                 "color": "#aaaaaa"
                    #                             },
                    #                             {
                    #                                 "type": "text",
                    #                                 "text": "14",
                    #                                 "size": "md",
                    #                                 "color": "#111111",
                    #                                 "align": "end"
                    #                             }
                    #                         ]
                    #                     },
                    #                     {
                    #                         "type": "box",
                    #                         "layout": "horizontal",
                    #                         "contents": [
                    #                             {
                    #                                 "type": "text",
                    #                                 "text": "สถานะอนุมัติ",
                    #                                 "size": "md",
                    #                                 "color": "#aaaaaa"
                    #                             },
                    #                             {
                    #                                 "type": "text",
                    #                                 "text": "อนุมัติแล้ว",
                    #                                 "size": "md",
                    #                                 "color": "#111111",
                    #                                 "align": "end"
                    #                             }
                    #                         ]
                    #                     },
                    #                     {
                    #                         "type": "separator",
                    #                         "margin": "xxl"
                    #                     },
                    #                     {
                    #                         "type": "box",
                    #                         "layout": "horizontal",
                    #                         "contents": [
                    #                             {
                    #                                 "type": "text",
                    #                                 "text": "วันที่ปฏิบัติงาน",
                    #                                 "size": "md",
                    #                                 "color": "#111111",
                    #                                 "flex": 0
                    #                             },
                    #                             {
                    #                                 "type": "text",
                    #                                 "text": "27/03/2020",
                    #                                 "size": "md",
                    #                                 "color": "#111111",
                    #                                 "align": "end",
                    #                                 "weight": "bold"
                    #                             }
                    #                         ],
                    #                         "margin": "md"
                    #                     },
                    #                     {
                    #                         "type": "box",
                    #                         "layout": "horizontal",
                    #                         "contents": [
                    #                             {
                    #                                 "type": "text",
                    #                                 "text": "เวลาเข้างาน",
                    #                                 "size": "md",
                    #                                 "color": "#aaaaaa"
                    #                             },
                    #                             {
                    #                                 "type": "text",
                    #                                 "text": "07:10:23",
                    #                                 "size": "md",
                    #                                 "color": "#111111",
                    #                                 "align": "end"
                    #                             }
                    #                         ]
                    #                     },
                    #                     {
                    #                         "type": "box",
                    #                         "layout": "horizontal",
                    #                         "contents": [
                    #                             {
                    #                                 "type": "text",
                    #                                 "text": "เวลาเลิกงาน",
                    #                                 "size": "md",
                    #                                 "color": "#aaaaaa"
                    #                             },
                    #                             {
                    #                                 "type": "text",
                    #                                 "text": "18:20:45",
                    #                                 "size": "md",
                    #                                 "color": "#111111",
                    #                                 "align": "end"
                    #                             }
                    #                         ]
                    #                     }
                    #                 ]
                    #             }
                    #         ],
                    #         "paddingBottom": "20px"
                    #     },
                    #     "footer": {
                    #         "type": "box",
                    #         "layout": "vertical",
                    #         "contents": [
                    #             {
                    #                 "type": "button",
                    #                 "action": {
                    #                     "type": "uri",
                    #                     "label": "สรุปการลงเวลางาน",
                    #                     "uri": "http://linecorp.com/"
                    #                 },
                    #                 "color": "#8448FF"
                    #             },
                    #             {
                    #                 "type": "button",
                    #                 "action": {
                    #                     "type": "uri",
                    #                     "label": "ส่งใบรับรองแพทย์",
                    #                     "uri": "http://linecorp.com/"
                    #                 },
                    #                 "color": "#8448FF"
                    #             },
                    #             {
                    #                 "type": "button",
                    #                 "action": {
                    #                     "type": "uri",
                    #                     "label": "รายละเอียดเพิ่มเติม",
                    #                     "uri": "http://linecorp.com/"
                    #                 },
                    #                 "style": "primary",
                    #                 "color": "#8448FF",
                    #                 "margin": "lg"
                    #             }
                    #         ]
                    #     },
                    #     "styles": {
                    #         "footer": {
                    #             "separator": True
                    #         }
                    #     }
                    # }
                    #
                    #                            )
                    #                            )
                except IndexError:
                    line_bot_api.reply_message(event.reply_token,
                                               TextSendMessage(
                                                   text='โปรดอัพเดท Daily update ก่อนนะครับ'))
                    print('Error profile: No daily update')

            elif dict_message['text'] == 'tracking':
                pass
            elif dict_message['text'] == 'สถานการณ์':
                pass
            elif dict_message['text'] == 'ช่วยเหลือ':
                pass
            elif dict_message['text'] == 'ใบเซ็นชื่อ':

                line_bot_api.reply_message(event.reply_token,
                                           FlexSendMessage(
                                               alt_text='hello',
                                               contents={
                                                   "type": "bubble",
                                                   "body": {
                                                       "type": "box",
                                                       "layout": "vertical",
                                                       "contents": [
                                                           {
                                                               "type": "image",
                                                               "size": "full",
                                                               "aspectMode": "cover",
                                                               "gravity": "center",
                                                               "url": "https://sv1.picz.in.th/images/2020/03/20/QiD33J.png",
                                                               "aspectRatio": "1:1"
                                                           },
                                                           {
                                                               "type": "image",
                                                               "url": "https://sv1.picz.in.th/images/2020/03/20/QiAZfS.png",
                                                               "aspectMode": "cover",
                                                               "size": "full",
                                                               "aspectRatio": "1040:174",
                                                               "action": {
                                                                   "type": "uri",
                                                                   "label": "action",
                                                                   "uri": "https://pea-covid19-test.herokuapp.com/checkin/{}/".format(
                                                                       user_employee.employee_ID)}
                                                           }
                                                       ],
                                                       "paddingAll": "0px"
                                                   }
                                               }
                                           )
                                           )
            elif dict_message['text'] == 'test2':
                line_bot_api.reply_message(event.reply_token,
                                           FlexSendMessage(
                                               alt_text='hello',
                                               contents={
                                                   "type": "carousel",
                                                   "contents": [
                                                       {
                                                           "type": "bubble",
                                                           "hero": {
                                                               "type": "image",
                                                               "size": "full",
                                                               "aspectRatio": "20:13",
                                                               "aspectMode": "cover",
                                                               "url": "https://s3-ap-southeast-1.amazonaws.com/img-in-th/022eb6b04e680592a3f0c340bd6c4954.png"
                                                           },
                                                           "body": {
                                                               "type": "box",
                                                               "layout": "vertical",
                                                               "spacing": "sm",
                                                               "contents": [
                                                                   {
                                                                       "type": "text",
                                                                       "text": "PEA Support",
                                                                       "wrap": True,
                                                                       "weight": "bold",
                                                                       "size": "xl"
                                                                   },
                                                                   {
                                                                       "type": "box",
                                                                       "layout": "baseline",
                                                                       "flex": 1,
                                                                       "contents": [
                                                                           {
                                                                               "type": "text",
                                                                               "text": "คู่มือปฏิบัติตัว COVID-19",
                                                                               "wrap": True,
                                                                               "weight": "bold",
                                                                               "size": "xl",
                                                                               "flex": 0
                                                                           }
                                                                       ]
                                                                   }
                                                               ]
                                                           },
                                                           "footer": {
                                                               "type": "box",
                                                               "layout": "vertical",
                                                               "spacing": "sm",
                                                               "contents": [
                                                                   {
                                                                       "type": "button",
                                                                       "flex": 2,
                                                                       "style": "primary",
                                                                       "color": "#aaaaaa",
                                                                       "action": {
                                                                           "type": "message",
                                                                           "label": "อ่านเลย",
                                                                           "text": "guidecovid"
                                                                       }
                                                                   }
                                                               ]
                                                           }
                                                       },
                                                       {
                                                           "type": "bubble",
                                                           "hero": {
                                                               "type": "image",
                                                               "size": "full",
                                                               "aspectRatio": "20:13",
                                                               "aspectMode": "cover",
                                                               "url": "https://s3-ap-southeast-1.amazonaws.com/img-in-th/6a77fcd94d5923db13d05d89748db110.png"
                                                           },
                                                           "body": {
                                                               "type": "box",
                                                               "layout": "vertical",
                                                               "spacing": "sm",
                                                               "contents": [
                                                                   {
                                                                       "type": "text",
                                                                       "text": "วิธีการใช้งาน",
                                                                       "wrap": True,
                                                                       "weight": "bold",
                                                                       "size": "xl"
                                                                   },
                                                                   {
                                                                       "type": "box",
                                                                       "layout": "baseline",
                                                                       "flex": 1,
                                                                       "contents": [
                                                                           {
                                                                               "type": "text",
                                                                               "text": "PEA COVID-19 LINE Official Account",
                                                                               "wrap": True,
                                                                               "weight": "regular",
                                                                               "size": "lg",
                                                                               "flex": 0
                                                                           }
                                                                       ]
                                                                   }
                                                               ]
                                                           },
                                                           "footer": {
                                                               "type": "box",
                                                               "layout": "vertical",
                                                               "spacing": "sm",
                                                               "contents": [
                                                                   {
                                                                       "type": "button",
                                                                       "flex": 2,
                                                                       "style": "primary",
                                                                       "color": "#aaaaaa",
                                                                       "action": {
                                                                           "type": "message",
                                                                           "label": "อ่านเลย",
                                                                           "text": "guide-line"
                                                                       }
                                                                   }
                                                               ]
                                                           }
                                                       },
                                                       {
                                                           "type": "bubble",
                                                           "hero": {
                                                               "type": "image",
                                                               "size": "full",
                                                               "aspectRatio": "20:13",
                                                               "aspectMode": "cover",
                                                               "url": "https://sv1.picz.in.th/images/2020/03/20/Qijv9I.png"
                                                           },
                                                           "body": {
                                                               "type": "box",
                                                               "layout": "vertical",
                                                               "spacing": "sm",
                                                               "contents": [
                                                                   {
                                                                       "type": "text",
                                                                       "text": "สายด่วน PEA",
                                                                       "wrap": True,
                                                                       "weight": "bold",
                                                                       "size": "xl"
                                                                   },
                                                                   {
                                                                       "type": "box",
                                                                       "layout": "baseline",
                                                                       "flex": 1,
                                                                       "contents": [
                                                                           {
                                                                               "type": "text",
                                                                               "text": "ติดต่อฉุกเฉิน โทร",
                                                                               "wrap": True,
                                                                               "weight": "regular",
                                                                               "size": "lg",
                                                                               "flex": 0
                                                                           }
                                                                       ]
                                                                   }
                                                               ]
                                                           },
                                                           "footer": {
                                                               "type": "box",
                                                               "layout": "vertical",
                                                               "spacing": "sm",
                                                               "contents": [
                                                                   {
                                                                       "type": "button",
                                                                       "flex": 2,
                                                                       "style": "primary",
                                                                       "action": {
                                                                           "type": "uri",
                                                                           "label": "ติดต่อฉุกเฉิน",
                                                                           "uri": "tel:1129"
                                                                       }
                                                                   }
                                                               ]
                                                           }
                                                       },
                                                       {
                                                           "type": "bubble",
                                                           "hero": {
                                                               "type": "image",
                                                               "size": "full",
                                                               "aspectRatio": "20:13",
                                                               "aspectMode": "cover",
                                                               "url": "https://sv1.picz.in.th/images/2020/03/20/Qil2IN.png"
                                                           },
                                                           "body": {
                                                               "type": "box",
                                                               "layout": "vertical",
                                                               "spacing": "sm",
                                                               "contents": [
                                                                   {
                                                                       "type": "text",
                                                                       "text": "กรมควบคุมโรค",
                                                                       "wrap": True,
                                                                       "weight": "bold",
                                                                       "size": "xl"
                                                                   },
                                                                   {
                                                                       "type": "box",
                                                                       "layout": "baseline",
                                                                       "contents": [
                                                                           {
                                                                               "type": "text",
                                                                               "text": "สายด่วน 1442",
                                                                               "wrap": True,
                                                                               "weight": "regular",
                                                                               "size": "lg",
                                                                               "flex": 0
                                                                           }
                                                                       ]
                                                                   }
                                                               ]
                                                           },
                                                           "footer": {
                                                               "type": "box",
                                                               "layout": "vertical",
                                                               "spacing": "sm",
                                                               "contents": [
                                                                   {
                                                                       "type": "button",
                                                                       "style": "primary",
                                                                       "action": {
                                                                           "type": "uri",
                                                                           "label": "ติดต่อฉุกเฉิน",
                                                                           "uri": "tel:1442"
                                                                       }
                                                                   }
                                                               ]
                                                           }
                                                       }
                                                   ]
                                               }
                                           )
                                           )
            else:
                line_bot_api.reply_message(event.reply_token,
                                           TextSendMessage(
                                               text='เพื่อการใช้งานที่ต่อเนื่อง และมีประสิทธิภาพ\n'
                                                    'หากอุปกรณ์ของคุณไม่รองรับปุ่มเมนู คุณสามารถเข้าถึงเมนูของเรา เพียงพิมพ์\n'
                                                    '1.“ขออนุมัติ” เพื่อเข้าสู่ระบบการแจ้งลาทั้งแบบป่วย COVID-19 หรือ ลาทำงานอยู่บ้าน (Work From Home)\n'
                                                    '2. “ช่วยเหลือ” เพื่อเข้าสู่ระบบศูนย์ช่วยเหลือ PEA COVID-19\n'
                                                    '3. “ประเมินความเสี่ยง” เพื่อเข้าสู่ระบบประเมินความเสี่ยงประจำวัน และตอบคำถามลุ้นรับรางวัลทุกวัน\n'
                                                    '4. “ข้อมูลส่วนตัว” เพื่อจัดการข้อมูลส่วนตัวของคุณ\n'
                                                    '5. “สถานการณ์” เพื่อเกาะติดสถานการณ์ COVID-19\n'
                                                    '6. “ใบเซ็นชื่อ” เพื่อเข้าระบบลงชื่อเข้าและเลิกทำงาน\nอย่าลืมเพิ่มระยะห่างทางสังคมนะครับ ถ้าเราไม่ติดกัน เราจะไม่ติดเชื้อ'))
        except ObjectDoesNotExist:
            line_bot_api.reply_message(event.reply_token,
                                       TextSendMessage(text='ไลน์ไอดีนี้ยังไม่ได้ลงทะเบียน โปรดพิมพ์รหัสพนักงาน 6 ตัว'))
            print('this line id has not registered yet')
        except MultipleObjectsReturned:
            line_bot_api.reply_message(event.reply_token,
                                       TextSendMessage(text='ไลน์ไอดีนี้มีมากกว่า 2 บัญชี โปรดแจ้ง admin ผ่านช่องทาง facebook PEA INNOVATION HUB https://www.facebook.com/peaihub/'))
            print('this line id has more than two account')


def send_question():
    to = 'Ud5a85712fadd31a77c26f24b0e73b74d'
    line_bot_api.push_message(to, TextSendMessage(text='Hello World!'))
