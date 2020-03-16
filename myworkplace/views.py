from django.shortcuts import render
from .models import employee

# Create your views here.
def home(request):
    data1 = employee.objects.all()
    context = {'number_of_employee': len(data1)}
    return render(request, 'myworkplace/home.html', context)

def daily_update(request, id):
    context = {'data': id}
    return render (request, 'myworkplace/daily_update.html', context)


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

    if dict_message['text']=='บันทึกรายวัน':
        employee_Line_ID_list = [x.employee_line_ID for x in employee.objects.all()]
        user_employee = employee.objects.get(employee_line_ID=dict_source['user_id'])
        print(user_employee)
        if dict_source['user_id'] in employee_Line_ID_list:

            line_bot_api.reply_message(event.reply_token,
                                       TextSendMessage(text=' www.https://pea-covid19-test.herokuapp.com/daily_update/{}'.format(user_employee.employee_ID)))
        else:
            line_bot_api.reply_message(event.reply_token,
                                       TextSendMessage(text='คุณยังไม่ได้ลงทะเบียน กรุณาป้อนรหัสพนักงาน 6 หลัก'))

    elif dict_message['text'].isnumeric() and len(dict_message['text'])==6: # check is number
        employee_Line_ID_list =[x.employee_line_ID for x in employee.objects.all()]
        if dict_source['user_id'] not in employee_Line_ID_list:  # check new customer
            new_user = employee(emplyee_name='blank', employee_line_ID=dict_source['user_id'],
                                employee_ID=dict_message['text'], activity_text='register', quarantined=False, infected=False)
            new_user.save()
            line_bot_api.reply_message(event.reply_token,
                                       TextSendMessage(text='ระบบได้ลงทะเบียนรหัสพนักงานนสำเร็จ'))

            # ส่งคำถามคัดกรอง

        else:  # existing customer
            line_bot_api.reply_message(event.reply_token,
                                       TextSendMessage(text='ไม่สามารถลงทะเบียนได้ไลน์ไอดีนี้ได้ลงทะเบียนแล้ว หากสงสัยติดต่อ admin'))
    else:
        line_bot_api.reply_message(event.reply_token,
                                           TextSendMessage(text='กรุณากรอกเลขรหัสพนักงาน 6 หลัก'))

    # else: # existing customer
    #     if dict_message['text']=='บริการพิเศษ':
    #         line_bot_api.reply_message(event.reply_token,
    #                                    TextSendMessage(text='working on it บริการพิเศษ'))
    #
    #     else:
    #         line_bot_api.reply_message(event.reply_token,
    #                                    TextSendMessage(text='กรุณากรอกเลขรหัสพนักงาน 6 หลัก'))

