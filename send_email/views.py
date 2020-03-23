from django.shortcuts import render
from exchangelib import Configuration, Account, DELEGATE, Credentials
from exchangelib import Message, Mailbox, FileAttachment
import requests, xmltodict
from datetime import datetime, timedelta
from myworkplace.models import employee, emailemployee
# Create your views here.

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
    # url = "https://idm.pea.co.th/webservices/EmployeeServices.asmx?WSDL"
    # headers = {'content-type': 'text/xml'}
    # xmltext = '''<?xml version="1.0" encoding="utf-8"?>
    #             <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    #             <soap:Body>
    #                 <GetEmployeeInfoByEmployeeId_SI xmlns="http://idm.pea.co.th/">
    #                 <WSAuthenKey>{0}</WSAuthenKey>
    #                 <EmployeeId>{1}</EmployeeId>
    #                 </GetEmployeeInfoByEmployeeId_SI>
    #             </soap:Body>
    #             </soap:Envelope>'''
    # wsauth = 'e7040c1f-cace-430b-9bc0-f477c44016c3'
    # body = xmltext.format(wsauth, "{}".format(id))
    # res = requests.post(url, data=body, headers=headers, timeout=1, allow_redirects=True)
    # o = xmltodict.parse(res.text)
    # jsonconvert = dict(o)
    # authData = jsonconvert["soap:Envelope"]['soap:Body']['GetEmployeeInfoByEmployeeId_SIResponse'][
    #     'GetEmployeeInfoByEmployeeId_SIResult']['ResultObject']
    #
    # return authData.get("Email")

    user = emailemployee.objects.get(employeeid=id)
    print(user.employeeemail)
    return user.employeeemail


#### สมัคร
def send_email_register(email, line_id, id):
    recipient_list = [email]
    print('receipient list', recipient_list)
    # subject = 'ยืนยันการสมัคร'
    # message = ' กดที่ link  https://pea-covid19-test.herokuapp.com/confirm_registration/{}{}'.format(line_id, id)
    server = 'email.pea.co.th'
    email = 'peacovid19@pea.co.th'
    username = 'peacovid19'
    password = 'peacovid19'
    account = connect(server, email, username, password)
    subject = 'ยืนยันการลงทะเบียน'
    body = ' รหัสพนักงานของท่าน {} ได้มีการลงทะเบียนกับ PEA COVID-19 ' \
           'กรุณาเริ่มต้นการใช้งาน โดยยืนยันตัวตนของท่านผ่านข้อความฉบับนี้โดยคลิกตาม link ด้านล่างนี้ ' \
           'https://pea-covid19-test.herokuapp.com/register/{}{} ' \
           'เพื่อกรอกข้อมูลส่วนตัว และประเมินคว่ามเสี่ยงเบื้องต้น ' \
           '' \
           'ขอขอบพระคุณที่ท่านร่วมเป็นส่วนหนึ่งกับเราในการฝ่าวิกฤติ COVID-19' \
           '' \
           'PEA COVID-19' \
           'By PEA Innovation Hub'.format(id, line_id, id)
    m = Message(account=account,
                subject=subject,
                body=body,
                to_recipients=recipient_list)
    print('message created')
    m.send_and_save()
    print(m)
    print('email send')


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


