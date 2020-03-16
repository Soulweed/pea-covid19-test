from django.shortcuts import render
from .models import employee

# Create your views here.
def home(request):
    data1 = employee.objects.all()
    context = {'number_of_employee': len(data1)}
    print(context)
    return render(request, 'myworkplace/home.html', context)







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


reply_text='A whole new world'
# # オウム返し
@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    print('Here is handle_text_message function')
    dict_event=event.__dict__
    print(dict_event)

    dict_source=dict_event['source'].__dict__
    dict_message=dict_event['message'].__dict__
    print(dict_message)


    if True: # new customer
        new_user = employee(emplyee_name='blank', employee_line_ID=dict_source['user_id'],
                            employee_ID=22222, activity_text='register', quarantined=False, infected=True)
        new_user.save()
        line_bot_api.reply_message(event.reply_token,
                                   TextSendMessage(text='ลงทะเบียนแล้ว'))
    else: # existing customer
        pass

# @handler.add(MessageEvent, message=TextMessage)
# def handle_text_message(event):
#     if event.message.text =='stock':
#         print('Here is handle_text_message function')
#         reply_text = ''
#         num = 1
#         for obj in queryset:
#             reply_text = reply_text + '{}. '.format(num)
#             reply_text = reply_text + 'Import date:{} type:{} class:{} weight:{} '.format(obj.create_at, obj.melon_type,
#                                                                                           obj.melon_class,
#                                                                                           obj.weight)
#             reply_text = reply_text + '       '
#             num += 1
#         line_bot_api.reply_message(event.reply_token,
#                                    TextSendMessage(text=reply_text))
