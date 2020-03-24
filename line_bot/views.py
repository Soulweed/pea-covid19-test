from django.shortcuts import render
from django.db import connection
from myworkplace.models import employee
from send_email.views import send_email_register, get_user_email

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
    print(body)
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
            employee.objects.get(employee_line_ID=dict_source['user_id'])
            connection.close()
            line_bot_api.reply_message(event.reply_token,
                                       TextSendMessage(text='ท่านได้ลงทะเบียนแล้ว'))
        except:
            email_name = get_user_email(id=dict_message['text'])
            if email_name is not None:
                try:
                    send_email_register(email=email_name, line_id=dict_source['user_id'], id=dict_message['text'])
                    line_bot_api.reply_message(event.reply_token,
                                               TextSendMessage(
                                                   text='โปรดทำงานยืนยันตัวตนของคุณผ่าน PEA Mail เพื่อเข้าสู่ระบบตาม link ด้านล่างนี้ https://email.pea.co.th '
                                                        '(username คือรหัสพนักงาน 6 หลัก)'),
                                               )
                except:
                    line_bot_api.reply_message(event.reply_token,
                                               TextSendMessage(text='ลองอีกครั้ง'))
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
    else:
        try:
            print(dict_source['user_id'])
            user_employee = employee.objects.get(employee_line_ID=dict_source['user_id'])
            connection.close()

            if dict_message['text'] == 'leave':
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
                                                                           "uri": "https://pea-covid19-test.herokuapp.com/"
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
                                                                           "uri": "https://pea-covid19-test.herokuapp.com/"
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
                # send_email_register(id = dict_message['text'], line_id=dict_source['user_id'])
                # print('ทดสอบ ส่งอีเมลแล้วเสร็จ')
            elif dict_message['text'] == 'check':
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
                                                                       "url": "https://sv1.picz.in.th/images/2020/03/19/QgvtPI.png",
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
                                                                           "uri": "https://pea-covid19-test.herokuapp.com/challenge2/{}/".format(
                                                                               user_employee.employee_ID)
                                                                       }
                                                                   }
                                                               ],
                                                               "paddingAll": "0px"
                                                           }
                                                       }
                                                   ]
                                               }
                                           ))
            elif dict_message['text'] == 'profile':
                line_bot_api.reply_message(event.reply_token,
                                           FlexSendMessage(
                                               alt_text='hello',
                                               contents={
                                                   "type": "bubble",
                                                   "hero": {
                                                       "type": "image",
                                                       "url": "https://sv1.picz.in.th/images/2020/03/19/QiOkcu.png",
                                                       "size": "full",
                                                       "action": {
                                                           "type": "uri",
                                                           "uri": "http://linecorp.com/"
                                                       },
                                                       "aspectMode": "cover",
                                                       "aspectRatio": "1040:677"
                                                   },
                                                   "body": {
                                                       "type": "box",
                                                       "layout": "vertical",
                                                       "contents": [
                                                           {
                                                               "type": "text",
                                                               "text": "{}".format(user_employee.emplyee_name),
                                                               "weight": "bold",
                                                               "size": "xl",
                                                               "align": "center"
                                                           },
                                                           {
                                                               "type": "text",
                                                               "text": "{}".format(user_employee.employee_ID),
                                                               "align": "center",
                                                               "size": "xl",
                                                               "weight": "bold"
                                                           },
                                                           {
                                                               "type": "box",
                                                               "layout": "horizontal",
                                                               "contents": [
                                                                   {
                                                                       "type": "text",
                                                                       "text": "ความเสี่ยง :",
                                                                       "size": "xl"
                                                                   },
                                                                   {
                                                                       "type": "text",
                                                                       "text": "{}".format(user_employee.healthy),
                                                                       "size": "xl"
                                                                   }
                                                               ],
                                                               "margin": "md"
                                                           },
                                                           {
                                                               "type": "box",
                                                               "layout": "horizontal",
                                                               "contents": [
                                                                   {
                                                                       "type": "text",
                                                                       "text": "สถานะ :",
                                                                       "size": "xl"
                                                                   },
                                                                   {
                                                                       "type": "text",
                                                                       "text": "{}".format(user_employee.active_status),
                                                                       "size": "xl"
                                                                   }
                                                               ],
                                                               "margin": "sm"
                                                           },
                                                           {
                                                               "type": "box",
                                                               "layout": "horizontal",
                                                               "contents": [
                                                                   {
                                                                       "type": "text",
                                                                       "text": "วันที่ประเมิน :",
                                                                       "size": "xl"
                                                                   },
                                                                   {
                                                                       "type": "text",
                                                                       "text": "19 มี.ค. 63",
                                                                       "size": "xl"
                                                                   }
                                                               ],
                                                               "margin": "sm"
                                                           },
                                                           {
                                                               "type": "box",
                                                               "layout": "horizontal",
                                                               "contents": [
                                                                   {
                                                                       "type": "text",
                                                                       "text": "เวลา",
                                                                       "size": "xl",
                                                                       "align": "start"
                                                                   },
                                                                   {
                                                                       "type": "text",
                                                                       "text": "10:30 น.",
                                                                       "size": "xl"
                                                                   }
                                                               ],
                                                               "margin": "sm"
                                                           },
                                                           {
                                                               "type": "box",
                                                               "layout": "horizontal",
                                                               "contents": [
                                                                   {
                                                                       "type": "text",
                                                                       "text": "เหลือเวลา",
                                                                       "size": "xl"
                                                                   },
                                                                   {
                                                                       "type": "text",
                                                                       "text": "12 วัน",
                                                                       "size": "xl"
                                                                   }
                                                               ],
                                                               "margin": "sm"
                                                           },
                                                           {
                                                               "type": "separator",
                                                               "margin": "xl"
                                                           },
                                                           {
                                                               "type": "button",
                                                               "action": {
                                                                   "type": "uri",
                                                                   "label": "รายละเอียดเพิ่มเติม",
                                                                   "uri": "http://pea-covid19-test.herokuapp.com/"
                                                               },
                                                               "margin": "xxl"
                                                           }
                                                       ],
                                                       "offsetTop": "-10px"
                                                   },
                                                   "size": "mega"
                                               }
                                           )
                                           )
            elif dict_message['text'] == 'tracking':
                pass
            elif dict_message['text'] == 'timestamp':
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
            elif dict_message['text'] == 'support':
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
                                               text='ฟังก์ชั่นนี้กำลังปรับปรุง ส่ง feedback ให้ admin ที่ www.menti.com กรอกรหัส 456368'))

        except:
            line_bot_api.reply_message(event.reply_token,
                                       # TextSendMessage(text='ไลน์ไอดีนี้ยังไม่ได้ลงทะเบียน โปรดกรอกรหัสพนักงาน 6 ตัว'))
            TextSendMessage(text='ตอนนี้ระบบปิดทำการชั่วคราวเพื่อปรับปรุงคร่าาา จะกลับมาอีกทีเร็วๆนี้'))



            # push message for question quarantile person
def send_question():
    to = 'Ud5a85712fadd31a77c26f24b0e73b74d'
    line_bot_api.push_message(to, TextSendMessage(text='Hello World!'))
