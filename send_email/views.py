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





#### สมัคร ยืนยัน Register
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
    body = ' รหัสพนักงานของท่าน {} ได้มีการลงทะเบียนกับ PEA COVID-19\n\n' \
           ' กรุณาเริ่มต้นการใช้งาน โดยยืนยันตัวตนของท่านผ่านข้อความฉบับนี้ โดยคลิกตาม link ด้านล่างนี้\n\n ' \
           ' https://pea-covid19-test.herokuapp.com/register/{} \n\n ' \
           'เพื่อกรอกข้อมูลส่วนตัว และประเมินความเสี่ยงเบื้องต้น \n\n ' \
           'ขอขอบพระคุณที่ท่านร่วมเป็นส่วนหนึ่งกับเรา ในการฝ่าวิกฤติ COVID-19 \n\n ' \
           'PEA COVID-19 \n ' \
           'By PEA Innovation Hub'.format(id, line_id, id)
    m = Message(account=account,
                subject=subject,
                body=body,
                to_recipients=recipient_list)
    print('message created')
    m.send_and_save()
    print(m)
    print('email send')



def send_email_wfh_request(id, boss):
    server = 'email.pea.co.th'
    email = 'peacovid19@pea.co.th'
    username = 'peacovid19'
    password = 'peacovid19'
    email_boss = boss + '@pea.co.th'
    account = connect(server, email, username, password)
    subject = 'ขอลา WFH'
    body = 'พนักงานรหัส {} ขอลา WFH กรุณากด link: https://pea-covid19-test.herokuapp.com/WFH_approve/{}/{}/'.format(id, id, boss)
    print(email_boss)

    m = Message(account=account,
                subject=subject,
                body=body,
                to_recipients=[email_boss])
    print('message created')
    m.send_and_save()
    print(m)
    print('email send')



def send_email_leave_request(id, boss):
    server = 'email.pea.co.th'
    email = 'peacovid19@pea.co.th'
    username = 'peacovid19'
    password = 'peacovid19'
    email_boss = boss + '@pea.co.th'
    account = connect(server, email, username, password)
    subject = 'ขอลา WFH'
    body = 'พนักงานรหัส {} ขอลา leave 14 วัน'.format(id)


    m = Message(account=account,
                subject=subject,
                body=body,
                to_recipients=[email_boss])
    print('message created')
    m.send_and_save()
    print(m)
    print('email send')


########################################### แจ้ง Boss ##########################################################
### แจ้งเตือน Boss พนักงานในสังกัดขาดการติดต่อระบบเกิน 3 วัน ไม่เข้าเกณฑ์กลุ่มเสี่ยง

def send_email_wfh_warning(request, id, boss, day):
    server = 'email.pea.co.th'
    email = 'peacovid19@pea.co.th'
    username = 'peacovid19'
    password = 'peacovid19'
    boss = boss + '@pea.co.th'
    account = connect(server, email, username, password)
    subject = 'แจ้งเตือน พนักงานในสังกัดท่านขาดการติดต่อกับระบบ Work from home'
    body = 'สวัสดีค่ะ \n\n' \
           'ระบบอัตโนมัติ PEA COVID-19 ขอแจ้งให้ทราบว่า\n\n ' \
           'ตามที่ {} รหัสพนักงาน {} ซึ่งเป็นพนักงานในสังกัดของท่าน ได้เข้าร่วมโครงการ Work from home' \
           'ภายใต้เงื่อนไขไม่เข้าเกณฑ์ผู้ป่วย CPVID-19 ตั้งแต่วันที่ {} ถึงวันที่ {} \n\n' \
           'ทางระบบได้ตรวจสอบพบว่าพนักงานคนดังกล่าว ไม่ได้ทำการติดต่อกับระบบต่อเนื่องเป็นระยะเวลา 3 วัน ตั้งแต่วันที่ {} ถึงวันที่ {} \n\n' \
           'จึงขอให้ท่านตรวจสอบสถานะของพนักงานในสังกัดของท่านและรายงานผลการติดตามโดยเร็วที่สุด กรุณากด link ด้านล่างเพื่อรายงานผล \n' \
           ' {} \n\n' \
           'ขอขอบคุณที่ท่านร่วมเป็นส่วนหนึ่งกับเรา \n'
    'ในการฝ่าวิกฤต COVID-19\n\n'
    'PEA COVID-19 \n ' \
    'By PEA Innovation Hub'.format(
        id, day, id, boss, day)


    m = Message(account=account,
                subject=subject,
                body=body,
                to_recipients=[boss])
    print('message created')
    m.send_and_save()
    print(m)
    print('email send')


# แจ้งเตือน Boss พนักงานไม่ได้ทำการติดต่อกับระบบเกิน 3 วัน เข้าเกณฑ์กลุ่มเสี่ยง
def send_email_leave(request, id, boss):
    server = 'email.pea.co.th'
    email = 'peacovid19@pea.co.th'
    username = 'peacovid19'
    password = 'peacovid19'
    account = connect(server, email, username, password)
    boss = boss + '@pea.co.th'

    subject = 'แจ้งเตือน พนักงานในสังกัดท่านขาดการติดต่อกับระบบ'
    body = 'สวัสดีค่ะ\n\n' \
           'ระบบอัตโนมัติ PEA COVID-19 ขอแจ้งให้ทราบว่า\n\n' \
           'ตามที่{}รหัสพนักงาน {} ซึ่งเป็นพนักงานในสังกัดของท่านได้เข้าร่วมโครงการ Work from home ภายใต้เงื่อนไขกลุ่มแยกตัวเอง 14 วัน COVID-19 ตั้งเเต่วันที่{}ถึงวันที่{}\n\n' \
           'ทางระบบได้ตรวจสอบพบว่าพนักงานคนดังกล่าว' \
           'ไม่ได้ทำการติดต่อกับระบบต่อเนื่องเป็นระยะเวลา 3 วัน ตั้งเเต่วันที่ {}ถึงวันที่ {}\n\n' \
           'จึงขอให้ท่านตรวจสอบสถานะของพนักงานในสังกัดของท่านและรายงานผลการติดตามโดยเร็วที่สุด กรุณากด link ด้านล่าง เพื่อรายงานผลhttps://pea-covid19-test.herokuapp.com/register/{}{}\n\n' \
           'ขอบคุณที่ท่านร่วมเป็นส่วนหนึ่งกับเราในการฝ่าวิกฤต COVID-19\n\n' \
           'PEA COVID-19\n' \
           'By PEA Innovation Hub'.format(id)
    m = Message(account=account,
                subject=subject,
                body=body,
                to_recipients=[boss])
    print('message created')
    m.send_and_save()
    print(m)
    print('email send')

    return render(request, 'myworkplace/confirm_WFH.html')


# แจ้งเตือน Boss พนักงานมีแนวโน้มออกนอกพื้นที่
def send_email_outgoing_warning(request, id, boss):
    server = 'email.pea.co.th'
    email = 'peacovid19@pea.co.th'
    username = 'peacovid19'
    password = 'peacovid19'
    account = connect(server, email, username, password)
    boss = boss + '@pea.co.th'

    subject = 'แจ้งเตือน พนักงานในสังกัดท่านมีแนวโน้มออกนอกพื้นที่'
    body = 'สวัสดีค่ะ\n\n' \
           'ระบบอัตโนมัติ PEA COVID-19 ได้ตรวจสอบพบว่า\n\n' \
           '{}รหัสพนักงาน {} ' \
           'ซึ่งเป็นพนักงานในสังกัดของท่าน' \
           'มีแนวโน้มออกนอกพื้นที่พักอาศัย ตามที่ได้ระบุไว้ในโครงการ Work from home ภายใต้เงื่อนไขต้องแยกตัวเอง 14 วัน\n\n' \
           'ขอให้ท่านดำเนินการติดตามตำแหน่งที่อยู่พนักงานคนดังกล่าว และรายงานผลติดตามโดยเร็วที่สุด กรุณากด link ด้านล่างเพื่อรายงานผลhttps://pea-covid19-test.herokuapp.com/register/{}{}\n\n' \
           'ขอบคุณที่ท่านร่วมเป็นส่วนหนึ่งกับเราในการฝ่าวิกฤต COVID-19\n\n' \
           'PEA COVID-19\n' \
           'By PEA Innovation Hub'.format(id)
    m = Message(account=account,
                subject=subject,
                body=body,
                to_recipients=[boss])
    print('message created')
    m.send_and_save()
    print(m)
    print('email send')

    return render(request, 'myworkplace/confirm_WFH.html')


########################################### แจ้งพนักงาน ##########################################################
# แจ้งเตือนพนักงานไม่ได้ทำการติดต่อกับระบบเกิน 3 วัน แยกตัวเอง
def send_email_leave(request, id, boss):
    server = 'email.pea.co.th'
    email = 'peacovid19@pea.co.th'
    username = 'peacovid19'
    password = 'peacovid19'
    account = connect(server, email, username, password)
    boss = boss + '@pea.co.th'

    subject = 'แจ้งเตือน ท่านขาดการติดต่อกับระบบ'
    body = 'สวัสดีค่ะ\n\n' \
           'ระบบอัตโนมัติ PEA COVID-19 ขอแจ้งให้ทราบว่า\n\n' \
           'ตามที่ท่านได้เข้าร่วมโครงการ Work from home ภายใต้เงื่อนไขกลุ่มแยกตัวเอง 14 วัน ตั้งเเต่วันที่{}ถึงวันที่{}\n\n' \
           'ทางระบบได้ตรวจสอบพบว่า' \
           'ท่านไม่ได้ทำการติดต่อกับระบบต่อเนื่องเป็นระยะเวลา 3 วัน ตั้งเเต่วันที่ {}ถึงวันที่ {}\n\n' \
           'ด้วยความห่วงใยสวัสดิภาพของพนักงาน ระบบจึงทำการรายงานไปยังผู้บังคับบัญาต้นสังกัดทราบเบื้องต้นเรียบร้อยแล้ว\n\n' \
           'ขอให้ท่านทำการบันทึกลงเวลาเข้างานในวันทำการถัดไป และรายงานสาเหตุที่ไม่ได้ลงเวลาปฏิบัติงานต่อผู้บังคับบัญชาทราบด้วยค่ะ\n\n' \
           'ขอบคุณที่ท่านร่วมเป็นส่วนหนึ่งกับเราในการฝ่าวิกฤต COVID-19\n\n' \
           'PEA COVID-19\n' \
           'By PEA Innovation Hub'.format(id)
    m = Message(account=account,
                subject=subject,
                body=body,
                to_recipients=[boss])
    print('message created')
    m.send_and_save()
    print(m)
    print('email send')

    return render(request, 'myworkplace/confirm_WFH.html')


# แจ้งเตือนพนักงานไม่ได้ทำการติดต่อกับระบบเกิน 3 วัน ไม่เข้าเกณฑ์ผู้ที่มีความเสี่ยง
def send_email_leave(request, id, boss):
    server = 'email.pea.co.th'
    email = 'peacovid19@pea.co.th'
    username = 'peacovid19'
    password = 'peacovid19'
    account = connect(server, email, username, password)
    boss = boss + '@pea.co.th'

    subject = 'แจ้งเตือน ท่านขาดการติดต่อกับระบบ'
    body = 'สวัสดีค่ะ\n\n' \
           'ระบบอัตโนมัติ PEA COVID-19 ขอแจ้งให้ทราบว่า\n\n' \
           'ตามที่ท่านได้เข้าร่วมโครงการ Work from home ภายใต้เงื่อนไขไม่เข้าเกณฑ์ผู้ที่มีความเสี่ยงต่อโรค COVID-19 ตั้งเเต่วันที่{}ถึงวันที่{}\n\n' \
           'ทางระบบได้ตรวจสอบพบว่า' \
           'ท่านไม่ได้ทำการติดต่อกับระบบต่อเนื่องเป็นระยะเวลา 3 วัน ตั้งเเต่วันที่ {}ถึงวันที่ {}\n\n' \
           'ทีมงาน PEA COVID-19 ห่วงใยสุขภาพของพนักงานทุกคน ระบบต้องการทราบข้อมูลการบันทึกลงเวลาปฏิบัติงาน Time Stamp และข้อมูล Daily Health Update ของท่านทุกวัน\n\n' \
           'ทั้งนี้ระบบได้ทำการรายงานไปยังผู้บังคับบัญชาต้นสังกัดของท่านให้ทราบเบื้องต้นเรียบร้อยแล้ว\n\n' \
           'ขอให้ท่านทำการบันทึกลงเวลาปฏิบัติงาน Time Stamp และข้อมูล Daily Health Update ในวันทำการถัดไป พร้อมทั้งรายงานสาเหตุที่ไม่ได้ทำการติดต่อกับระบบต่อผู้บังคับบัญชารับทราบด้วยค่ะ\n\n' \
           'ขอบคุณที่ท่านร่วมเป็นส่วนหนึ่งกับเราในการฝ่าวิกฤต COVID-19\n\n' \
           'PEA COVID-19\n' \
           'By PEA Innovation Hub'.format(id)
    m = Message(account=account,
                subject=subject,
                body=body,
                to_recipients=[boss])
    print('message created')
    m.send_and_save()
    print(m)
    print('email send')

    return render(request, 'myworkplace/confirm_WFH.html')


### แจ้งเตือน พนักงาน ขาดการทำ Time Stamp

def send_email_timestamp_warning(request, id, boss, day):
    server = 'email.pea.co.th'
    email = 'peacovid19@pea.co.th'
    username = 'peacovid19'
    password = 'peacovid19'
    boss = boss + '@pea.co.th'
    account = connect(server, email, username, password)
    subject = 'แจ้งเตือน ท่านขาดการบันทึกเวลาปฏิบัติงาน'
    body = 'สวัสดีค่ะ \n\n' \
           'ตามที่ท่านได้เข้าร่วมโครงการ Work from home ภายใต้เงื่อนไขแยกตัวเอง 14 วัน ตั้งแต่วันที่ {} ถึงวันที่ {} \n\n ' \
           'ระบบอัตโนมัติ PEA COVID-19 ได้ตรวจสอบพบว่า' \
           'ท่านไม่ได้ทำการบันทึกเวลาปฏิบัติงาน Time Stamp ในวันที่ {} \n\n' \
           'ทีมงาน PEA COVID-19 ห่วงใยสุขภาพพนักงานทุกท่าน ระบบต้องการทราบข้อมูลการบันทึกเวลาปฏิบัติงาน Time Stamp, ข้อมูล Daily Health Update และ PEA STOP COVID-19 CHALLENGE ของท่านทุกวัน  \n\n' \
           'ขอให้ท่านทำการบันทึกเวลาปฏิบัติงาน Time Stamp, บันทึก Daily Health Update และ PEA STOP COVID-19 CHALLENGE ในวันถัดไป และรายงานสาเหตุที่ไม่ได้ลงเวลาปฏิบัติงานต่อผู้บังคับบัญชารับทราบด้วยค่ะ \n\n' \
           '* ทั้งนี้หากท่านขาดการติดต่อกับระบบต่อเนื่องเป็นระยะเวลา 3 วัน ระบบจะแจ้งเตือนไปยังผู้บังคับบัญชาต้นสังกัดของท่านต่อไป \n\n' \
           'ขอขอบคุณที่ท่านร่วมเป็นส่วนหนึ่งกับเรา \n'
    'ในการฝ่าวิกฤต COVID-19\n\n'
    'PEA COVID-19 \n ' \
    'By PEA Innovation Hub'.format(
        id, day, id, boss, day)


    m = Message(account=account,
                subject=subject,
                body=body,
                to_recipients=[boss])
    print('message created')
    m.send_and_save()
    print(m)
    print('email send')


### แจ้งเตือน พนักงาน ขาดการทำ PEA STOP COVID-19 CHALLENGE

def send_email_challenge_warning(request, id, boss, day):
    server = 'email.pea.co.th'
    email = 'peacovid19@pea.co.th'
    username = 'peacovid19'
    password = 'peacovid19'
    boss = boss + '@pea.co.th'
    account = connect(server, email, username, password)
    subject = 'แจ้งเตือน ท่านขาดการเข้าร่วม PEA STOP COVID-19 CHALLENGE'
    body = 'สวัสดีค่ะ \n\n' \
           'ตามที่ท่านได้เข้าร่วมโครงการ Work from home ภายใต้เงื่อนไขแยกตัวเอง 14 วัน ตั้งแต่วันที่ {} ถึงวันที่ {} \n\n ' \
           'ระบบอัตโนมัติ PEA COVID-19 ได้ตรวจสอบพบว่า' \
           'ท่านไม่ได้ทำการเข้าร่วม PEA STOP COVID-19 CHALLENGE ในวันที่ {} \n\n' \
           'ทีมงาน PEA COVID-19 ห่วงใยสุขภาพพนักงานทุกท่าน ระบบต้องการทราบข้อมูลการบันทึกเวลาปฏิบัติงาน Time Stamp, ข้อมูล Daily Health Update และ PEA STOP COVID-19 CHALLENGE ของท่านทุกวัน  \n\n' \
           'ขอให้ท่านทำการบันทึกเวลาปฏิบัติงาน Time Stamp, บันทึก Daily Health Update และ PEA STOP COVID-19 CHALLENGE ในวันถัดไป และรายงานสาเหตุที่ไม่ได้ลงเวลาปฏิบัติงานต่อผู้บังคับบัญชารับทราบด้วยค่ะ \n\n' \
           '* ทั้งนี้หากท่านขาดการติดต่อกับระบบต่อเนื่องเป็นระยะเวลา 3 วัน ระบบจะแจ้งเตือนไปยังผู้บังคับบัญชาต้นสังกัดของท่านต่อไป \n\n' \
           'ขอขอบคุณที่ท่านร่วมเป็นส่วนหนึ่งกับเรา \n'
    'ในการฝ่าวิกฤต COVID-19\n\n'
    'PEA COVID-19 \n ' \
    'By PEA Innovation Hub'.format(
        id, day, id, boss, day)


    m = Message(account=account,
                subject=subject,
                body=body,
                to_recipients=[boss])
    print('message created')
    m.send_and_save()
    print(m)
    print('email send')


### แจ้งเตือน พนักงาน ขาดการทำ Daily Health Update

def send_email_dailyhealth_warning(request, id, boss, day):
    server = 'email.pea.co.th'
    email = 'peacovid19@pea.co.th'
    username = 'peacovid19'
    password = 'peacovid19'
    boss = boss + '@pea.co.th'
    account = connect(server, email, username, password)
    subject = 'แจ้งเตือน ท่านขาดการเข้าร่วม Daily Health Update'
    body = 'สวัสดีค่ะ \n\n' \
           'ตามที่ท่านได้เข้าร่วมโครงการ Work from home ภายใต้เงื่อนไขแยกตัวเอง 14 วัน ตั้งแต่วันที่ {} ถึงวันที่ {} \n\n ' \
           'ระบบอัตโนมัติ PEA COVID-19 ได้ตรวจสอบพบว่า' \
           'ท่านไม่ได้ทำการบันทึก Daily Health Update ในวันที่ {} \n\n' \
           'ทีมงาน PEA COVID-19 ห่วงใยสุขภาพพนักงานทุกท่าน ระบบต้องการทราบข้อมูลการบันทึกเวลาปฏิบัติงาน Time Stamp, ข้อมูล Daily Health Update และ PEA STOP COVID-19 CHALLENGE ของท่านทุกวัน  \n\n' \
           'ขอให้ท่านทำการบันทึกเวลาปฏิบัติงาน Time Stamp, บันทึก Daily Health Update และ PEA STOP COVID-19 CHALLENGE ในวันถัดไป และรายงานสาเหตุที่ไม่ได้ลงเวลาปฏิบัติงานต่อผู้บังคับบัญชารับทราบด้วยค่ะ \n\n' \
           '* ทั้งนี้หากท่านขาดการติดต่อกับระบบต่อเนื่องเป็นระยะเวลา 3 วัน ระบบจะแจ้งเตือนไปยังผู้บังคับบัญชาต้นสังกัดของท่านต่อไป \n\n' \
           'ขอขอบคุณที่ท่านร่วมเป็นส่วนหนึ่งกับเรา \n'
    'ในการฝ่าวิกฤต COVID-19\n\n'
    'PEA COVID-19 \n ' \
    'By PEA Innovation Hub'.format(
        id, day, id, boss, day)


    m = Message(account=account,
                subject=subject,
                body=body,
                to_recipients=[boss])
    print('message created')
    m.send_and_save()
    print(m)
    print('email send')


### แจ้งเตือน พนักงาน ขาดการทำ Time Stamp, PEA STOP COVID-19 CHALLENGE, Daily Health Update

def send_email_activity_warning(request, id, boss, day):
    server = 'email.pea.co.th'
    email = 'peacovid19@pea.co.th'
    username = 'peacovid19'
    password = 'peacovid19'
    boss = boss + '@pea.co.th'
    account = connect(server, email, username, password)
    subject = 'แจ้งเตือน ท่านขาดการติดต่อกับระบบ Work from home'
    body = 'สวัสดีค่ะ \n\n' \
           'ตามที่ท่านได้เข้าร่วมโครงการ Work from home ภายใต้เงื่อนไขแยกตัวเอง 14 วัน ตั้งแต่วันที่ {} ถึงวันที่ {} \n\n ' \
           'ระบบอัตโนมัติ PEA COVID-19 ได้ตรวจสอบพบว่า' \
           'ท่านไม่ได้ทำการบันทึกเวลาปฏิบัติงาน Time Stamp, Daily Health Update และ PEA STOP COVID-19 CHALLENGE ในวันที่ {} \n\n' \
           'ทีมงาน PEA COVID-19 ห่วงใยสุขภาพพนักงานทุกท่าน ระบบต้องการทราบข้อมูลการบันทึกเวลาปฏิบัติงาน Time Stamp, ข้อมูล Daily Health Update และ PEA STOP COVID-19 CHALLENGE ของท่านทุกวัน  \n\n' \
           'ขอให้ท่านทำการบันทึกเวลาปฏิบัติงาน Time Stamp, บันทึก Daily Health Update และ PEA STOP COVID-19 CHALLENGE ในวันถัดไป และรายงานสาเหตุที่ไม่ได้ลงเวลาปฏิบัติงานต่อผู้บังคับบัญชารับทราบด้วยค่ะ \n\n' \
           '* ทั้งนี้หากท่านขาดการติดต่อกับระบบต่อเนื่องเป็นระยะเวลา 3 วัน ระบบจะแจ้งเตือนไปยังผู้บังคับบัญชาต้นสังกัดของท่านต่อไป \n\n' \
           'ขอขอบคุณที่ท่านร่วมเป็นส่วนหนึ่งกับเรา \n'
    'ในการฝ่าวิกฤต COVID-19\n\n'
    'PEA COVID-19 \n ' \
    'By PEA Innovation Hub'.format(
        id, day, id, boss, day)


    m = Message(account=account,
                subject=subject,
                body=body,
                to_recipients=[boss])
    print('message created')
    m.send_and_save()
    print(m)
    print('email send')
