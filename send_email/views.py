from django.shortcuts import render
from django.db import connection


from exchangelib import Configuration, Account, DELEGATE, Credentials
from exchangelib import Message, Mailbox, FileAttachment, protocol
from exchangelib.errors import UnauthorizedError, TransportError, RedirectError, RelativeRedirect
from exchangelib.protocol import BaseProtocol, NoVerifyHTTPAdapter

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
    url = "http://pealife-ms.pea.co.th/api/Covid19/GetEmployeeDetail/"

    payload = "{EmployeeID:\"%s\",ApiKey:\"fHC25Bp7cOj4oFuTF3dBMozOjMH1O8xj\"}\n" %(id)
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload).json()

    first_name = response['data']['dataDetail'][0]['first_name']
    last_name = response['data']['dataDetail'][0]['last_name']
    sex_desc = response['data']['dataDetail'][0]['sex_desc']
    posi_text_short = response['data']['dataDetail'][0]['posi_text_short']
    dept_sap_short=response['data']['dataDetail'][0]['dept_sap_short']
    dept_sap = response['data']['dataDetail'][0]['dept_sap']
    dept_upper = response['data']['dataDetail'][0]['dept_upper']
    sub_region = response['data']['dataDetail'][0]['sub_region']
    email = response['data']['dataDetail'][0]['email']

    return first_name, last_name, sex_desc, posi_text_short, dept_sap_short, dept_sap, dept_upper, sub_region, email




def get_user_email2(id):
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

#### สมัคร ยืนยัน Register
def send_email_register(emp_email, line_id, id):
    recipient_list = [emp_email]
    print('receipient list', recipient_list)

    server = 'email.pea.co.th'
    email = 'peacovid19@pea.co.th'
    username = 'peacovid19'
    password = 'peacovid19'
    account = connect(server, email, username, password)
    subject = 'ยืนยันการลงทะเบียน'
    body = 'รหัสพนักงานของท่าน {} ได้มีการลงทะเบียนกับ PEA COVID-19\n\n' \
           'กรุณาเริ่มต้นการใช้งาน โดยยืนยันตัวตนของท่านผ่านข้อความฉบับนี้ โดยคลิกตาม link ด้านล่างนี้\n\n ' \
           'https://pea-covid19-test.herokuapp.com/register/{}{}/ \n\n' \
           'เพื่อกรอกข้อมูลส่วนตัว และประเมินความเสี่ยงเบื้องต้น \n\n' \
           'ขอขอบพระคุณที่ท่านร่วมเป็นส่วนหนึ่งกับเรา ในการผ่านวิกฤติ COVID-19 ไปด้วยกัน\n\n' \
           'PEA COVID-19 \n' \
           'By PEA Innovation Hub'.format(id, line_id, id)
    m = Message(account=account,
                subject=subject,
                body=body,
                to_recipients=recipient_list)
    m.send_and_save()
    protocol.close_connections()

    # m.close()
    print('email register send: {} : {}'.format(id, emp_email))


def send_email_confrim_register(emp_id, emp_email):
    recipient_list = [emp_email]
    print('receipient list', recipient_list)
    # subject = 'ยืนยันการสมัคร'
    # message = ' กดที่ link  https://pea-covid19-test.herokuapp.com/confirm_registration/{}{}'.format(line_id, id)
    server = 'email.pea.co.th'
    email = 'peacovid19@pea.co.th'
    username = 'peacovid19'
    password = 'peacovid19'
    account = connect(server, email, username, password)
    subject = 'ยืนยันการลงทะเบียน'
    body='ขอบคุณที่ร่วมลงทะเบียนกับเรา \n\nรหัสพนักงานของท่านได้ทำการลงทะเบียนในระบบ PEA COVID-19 LINE Official Account สำเร็จแล้ว\n\n' \
         'วิธีการใช้งานเบื้องต้น\n\n'\
         'เพื่อการใช้งานที่ต่อเนื่อง และมีประสิทธิภาพ หากอุปกรณ์ของคุณไม่รองรับปุ่มเมนู (เช่นใช้งานบน Tablet, iPad, LINE PC)\n\n' \
         'คุณสามารถเข้าถึงเมนูของเราเพียง พิมพ์ข้อความ\n\n' \
         '1. “ขออนุมัติ” เพื่อเข้าสู่ระบบการแจ้งลาทั้งแบบป่วย COVID-19 หรือ ลาทำงานอยู่บ้าน (Work From Home)\n\n' \
         '2. “ช่วยเหลือ” เพื่อเข้าสู่ระบบศูนย์ช่วยเหลือ PEA COVID-19\n\n' \
         '3. “ประเมินความเสี่ยง” เพื่อเข้าสู่ระบบประเมินความเสี่ยงประจำวัน และตอบคำถามลุ้นรับรางวัลทุกวัน\n\n' \
         '4. “ข้อมูลส่วนตัว” เพื่อจัดการข้อมูลส่วนตัวของคุณ\n\n' \
         '5. “สถานการณ์” เพื่อเกาะติดสถานการณ์ COVID-19\n\n' \
         '6. “ใบเซ็นชื่อ” เพื่อเข้าระบบลงชื่อเข้าและเลิกทำงาน\n\n' \
         'อย่าลืมเพิ่มระยะห่างทางสังคมนะครับ ถ้าเราไม่ติดกัน เราจะไม่ติดเชื้อ\n\n' \
         'ขอขอบพระคุณที่ท่านร่วมเป็นส่วนหนึ่งกับเรา ในการผ่านวิกฤติ COVID-19 ไปด้วยกัน\n\n' \
         'PEA COVID-19\n' \
         'By PEA Innovation Hub'

    m = Message(account=account,
                subject=subject,
                body=body,
                to_recipients=recipient_list)
    # print('message created')
    m.send_and_save()
    protocol.close_connections()

    # print(m)
    print('email confirm register send: {} : {}'.format(emp_id, emp_email))


def send_email_wfh_request(id, email_boss, total_date, name, startdate,enddate):
    recipient_list = [email_boss]
    print('receipient list', recipient_list)

    server = 'email.pea.co.th'
    email = 'peacovid19@pea.co.th'
    username = 'peacovid19'
    password = 'peacovid19'
    account = connect(server, email, username, password)
    # email_boss = boss + '@pea.co.th'
    boss=email_boss[0:-5]
    subject = 'ขออนุมัติ Work from Home'
    body = 'ระบบอัตโนมัติ PEA COVID-19 ได้รับแจ้งจากชื่อ  {} รหัสพนักงาน {} มีความประสงค์ขอปฏิบัติงานแบบ Work from home เงื่อนไขไม่เข้าเกณฑ์ผู้ที่มีความเสี่ยงต่อโรค COVID-19 \n\n' \
           'ระหว่างวันที่ {} ถึงวันที่ {} รวมระยะเวลาทั้งหมด {} วัน \n\n' \
           'ขอให้ท่านพิจารณาอนุมัติการปฏิบัติงานแบบ Work from home ให้พนักงานในสังกัดของท่าน\n\n' \
           'หากท่านพิจารณาแล้วเห็นสมควร "อนุมัติ" ให้คลิกตาม link ด้านล่างนี้ \n\n' \
           'https://pea-covid19-test.herokuapp.com/WFH_approve/{}/{}/{}/\n\n' \
           'ขอขอบพระคุณที่ท่านร่วมเป็นส่วนหนึ่งกับเรา ในการผ่านวิกฤติ COVID-19 ไปด้วยกัน\n\n' \
           'PEA COVID-19\n' \
           'By PEA Innovation Hub'.format(name, id, startdate, enddate, total_date, id, boss, total_date)
    m = Message(account=account,
                subject=subject,
                body=body,
                to_recipients=recipient_list)
    # print('message created')
    m.send_and_save()
    protocol.close_connections()

    # print(m)
    print('email wfh request send: {} >> {}'.format(id, email_boss))


def send_email_confrim_wfh(boss, emp_email):
    recipient_list = [emp_email]
    # print('receipient list', recipient_list)
    # subject = 'ยืนยันการสมัคร'
    # message = ' กดที่ link  https://pea-covid19-test.herokuapp.com/confirm_registration/{}{}'.format(line_id, id)
    server = 'email.pea.co.th'
    email = 'peacovid19@pea.co.th'
    username = 'peacovid19'
    password = 'peacovid19'
    account = connect(server, email, username, password)
    subject = 'แจ้งผลการอนุมัติ Work from home'
    body='คำร้องการขอปฏิบัติงานแบบ Work From Home ของท่านได้รับการอนุมัติจากผู้บังคับบัญชาต้นสังกัดแล้ว\n\n' \
         'สามารถดูข้อมูลเพิ่มเติมได้ที่ LINE: PEA COVID-19 โดยเข้าไปที่เมนู "ข้อมูลส่วนตัว"\n\n' \
         'อย่าลืมลงบันทึกเวลาปฏิบัติงานและประเมินความเสี่ยงประจำวันผ่านระบบ PEA COVID-19 ด้วยนะครับ\n\n' \
         'ขอขอบพระคุณที่ท่านร่วมเป็นส่วนหนึ่งกับเรา ในการผ่านวิกฤติ COVID-19 ไปด้วยกัน\n\n' \
         'PEA COVID-19\n' \
         'By PEA Innovation Hub'

    m = Message(account=account,
                subject=subject,
                body=body,
                to_recipients=recipient_list)
    # print('message created')
    m.send_and_save()
    protocol.close_connections()

    # print(m)
    print('email confrim wfh send: {} >> {}'.format(boss, emp_email))


def send_email_wfh14day_request(id, email_boss, name, startdate, enddate):
    recipient_list = [email_boss]
    # print('receipient list', recipient_list)
    server = 'email.pea.co.th'
    email = 'peacovid19@pea.co.th'
    username = 'peacovid19'
    password = 'peacovid19'
    account = connect(server, email, username, password)
    # email_boss = boss + '@pea.co.th'
    subject = 'ขออนุมัติ Work from home เพื่อแยกตัวเอง 14 วัน'
    body = 'ระบบอัตโนมัติ PEA COVID-19 ได้รับแจ้งจาก {} รหัสพนักงาน {} \n\n' \
           'มีความประสงค์ขอปฏิบัติงานแบบ Work from home เพื่อขอแยกตัวเอง เนื่องจากมีความเสี่ยงในการสัมผัสเชื้อโรค COVID-19 เป็นเวลา 14 วัน ตั้งแต่วันที่ {} ถึงวันที่ {} ' \
           'ขอให้ท่านพิจารณาอนุมัติการปฏิบัติงานแบบ Work from home ให้พนักงานในสังกัดของท่าน\n\n' \
           'หากท่านพิจารณาแล้วเห็นสมควร "อนุมัติ" ให้คลิกตาม link ด้านล่างนี้ \n\n' \
           'https://pea-covid19-test.herokuapp.com/WFH_approve/{}/{}/{}/\n\n' \
           'ขอขอบพระคุณที่ท่านร่วมเป็นส่วนหนึ่งกับเรา ในการผ่านวิกฤติ COVID-19 ไปด้วยกัน\n' \
           'PEA COVID-19\n' \
           'By PEA Innovation Hub'.format(name, id, startdate, enddate, id, email_boss, 14)
    m = Message(account=account,
                subject=subject,
                body=body,
                to_recipients=recipient_list)
    # print('message created')
    m.send_and_save()
    protocol.close_connections()

    # print(m)
    print('email send: {} >> {}'.format(id, email_boss))


def send_email_meetdoc_request(id, email_boss, name):
    try:
        recipient_list = [email_boss]
        # print('receipient list', recipient_list)
        server = 'email.pea.co.th'
        email = 'peacovid19@pea.co.th'
        username = 'peacovid19'
        password = 'peacovid19'

        BaseProtocol.USERAGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
        BaseProtocol.HTTP_ADAPTER_CLS = NoVerifyHTTPAdapter

        account = connect(server, email, username, password)
        # email_boss = boss + '@pea.co.th'
        subject = 'ขอลาป่วย 14 วัน'
        body = 'ระบบอัตโนมัติ PEA COVID-19 ได้รับแจ้งจาก  {}  รหัส {} ซึ่งเป็นพนักงานในสังกัดของท่าน มีความเสี่ยงในการติดเชื้อ COVID-19 ต้องแยกตัวเอง เพื่อเฝ้าดูอาการและควรพบแพทย์\n\n' \
               'ขอให้ท่านติดตามอาการพนักงานในสังกัดของท่านอย่างใกล้ชิด \n\n' \
               'ขอขอบพระคุณที่ท่านร่วมเป็นส่วนหนึ่งกับเรา ในการผ่านวิกฤติ COVID-19 ไปด้วยกัน\n' \
               'PEA COVID-19\n' \
               'By PEA Innovation Hub'.format(name, id)
        m = Message(account=account,
                    subject=subject,
                    body=body,
                    to_recipients=recipient_list)
        # print('message created')

        m.send_and_save()
        protocol.close_connections()
        print('email send: {} >> {}'.format(id, email_boss))
        return True
        # print(m)

    except Exception as e:
        print(" >>>> Fail: {}".format(e))
        return False


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
    body = 'ระบบอัตโนมัติ PEA COVID-19 ขอแจ้งให้ทราบว่า\n\n ' \
           'ตามที่ {} รหัสพนักงาน {} ซึ่งเป็นพนักงานในสังกัดของท่าน ได้เข้าร่วมโครงการ Work from home' \
           'ภายใต้เงื่อนไขไม่เข้าเกณฑ์ผู้ป่วย CPVID-19 ตั้งแต่วันที่ {} ถึงวันที่ {} \n\n' \
           'ทางระบบได้ตรวจสอบพบว่า พนักงานคนดังกล่าว ไม่ได้ทำการติดต่อกับระบบต่อเนื่องเป็นระยะเวลา 3 วัน ตั้งแต่วันที่ {} ถึงวันที่ {} \n\n' \
           'จึงขอให้ท่านตรวจสอบสถานะของพนักงานในสังกัดของท่านและรายงานผลการติดตามโดยเร็วที่สุด \n\n' \
           'โดยคลิกตาม link ด้านล่างเพื่อรายงานผล \n' \
           ' {} \n\n' \
           'ขอขอบพระคุณที่ท่านร่วมเป็นส่วนหนึ่งกับเรา ในการผ่านวิกฤติ COVID-19 ไปด้วยกัน\n' \
           'PEA COVID-19 \n ' \
           'By PEA Innovation Hub'.format(
        id, day, id, boss, day)


    m = Message(account=account,
                subject=subject,
                body=body,
                to_recipients=[boss])
    # print('message created')
    m.send_and_save()
    # print(m)
    print('email send: {} >> {}'.format(id, boss))


# แจ้งเตือน Boss พนักงานไม่ได้ทำการติดต่อกับระบบเกิน 3 วัน เข้าเกณฑ์กลุ่มเสี่ยง
def send_email_leave(request, id, boss):
    server = 'email.pea.co.th'
    email = 'peacovid19@pea.co.th'
    username = 'peacovid19'
    password = 'peacovid19'
    account = connect(server, email, username, password)
    boss = boss + '@pea.co.th'

    subject = 'แจ้งเตือน พนักงานในสังกัดท่านขาดการติดต่อกับระบบ'
    body = 'ระบบอัตโนมัติ PEA COVID-19 ขอแจ้งให้ทราบว่า\n\n' \
           'ตามที่ {} รหัสพนักงาน {} ซึ่งเป็นพนักงานในสังกัดของท่านได้เข้าร่วมโครงการ Work from home เนื่องจากมีความเสี่ยงในการสัมผัสเชื้อโรค COVID-19 เป็นเวลา 14 วัน ตั้งเเต่วันที่ {} ถึงวันที่ {}\n\n' \
           'ทางระบบได้ตรวจสอบพบว่าพนักงานคนดังกล่าว' \
           'ไม่ได้ทำการติดต่อกับระบบต่อเนื่องเป็นระยะเวลา 3 วัน ตั้งแต่วันที่ {} ถึงวันที่ {}\n\n' \
           'จึงขอให้ท่านตรวจสอบสถานะของพนักงานในสังกัดของท่านและรายงานผลการติดตามโดยเร็วที่สุด\n\n' \
           'โดยคลิกตาม link ด้านล่าง เพื่อรายงานผล \n\n'\
           'https://pea-covid19-test.herokuapp.com/register/{}{}\n\n' \
           'ขอขอบพระคุณที่ท่านร่วมเป็นส่วนหนึ่งกับเรา ในการผ่านวิกฤติ COVID-19 ไปด้วยกัน\n\n' \
           'PEA COVID-19\n' \
           'By PEA Innovation Hub'.format(id)
    m = Message(account=account,
                subject=subject,
                body=body,
                to_recipients=[boss])
    # print('message created')
    m.send_and_save()
    # print(m)
    print('email send: {} >> {}'.format(id, boss))

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
    body = 'ระบบอัตโนมัติ PEA COVID-19 ได้ตรวจสอบพบว่า\n\n' \
           '{}รหัสพนักงาน {} ซึ่งเป็นพนักงานในสังกัดของท่าน \n\n' \
           'มีแนวโน้มออกนอกพื้นที่พักอาศัย ตามที่ได้ระบุไว้ในโครงการ Work from home เนื่องจากมีความเสี่ยงในการสัมผัสเชื้อโรค COVID-19 เป็นเวลา 14 วัน\n\n' \
           'ขอให้ท่านดำเนินการติดตามตำแหน่งที่อยู่พนักงานคนดังกล่าว และรายงานผลติดตามโดยเร็วที่สุด \n\n' \
           'โดยคลิกตาม link ด้านล่าง เพื่อรายงานผล \n\n'\
           'https://pea-covid19-test.herokuapp.com/register/{}{}\n\n' \
           'ขอขอบพระคุณที่ท่านร่วมเป็นส่วนหนึ่งกับเรา ในการผ่านวิกฤติ COVID-19 ไปด้วยกัน\n\n' \
           'PEA COVID-19\n' \
           'By PEA Innovation Hub'.format(id)
    m = Message(account=account,
                subject=subject,
                body=body,
                to_recipients=[boss])
    # print('message created')
    m.send_and_save()
    # print(m)
    print('email send: {} >> {}'.format(id, boss))

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
    body = 'ระบบอัตโนมัติ PEA COVID-19 ขอแจ้งให้ทราบว่า\n\n' \
           'ตามที่ท่านได้เข้าร่วมโครงการ Work from home เนื่องจากมีความเสี่ยงในการสัมผัสเชื้อโรค COVID-19 เป็นเวลา 14 วัน ตั้งแต่วันที่ {} ถึงวันที่ {}\n\n' \
           'ทางระบบได้ตรวจสอบพบว่า' \
           'ท่านไม่ได้ทำการติดต่อกับระบบต่อเนื่องเป็นระยะเวลา 3 วัน ตั้งแต่วันที่ {} ถึงวันที่ {}\n\n' \
           'ด้วยความห่วงใยสวัสดิภาพของพนักงาน ระบบจึงทำการรายงานไปยังผู้บังคับบัญาต้นสังกัดทราบเรียบร้อยแล้ว\n\n' \
           'ขอให้ท่านทำการบันทึกลงเวลาเข้า-เลิกงานในวันทำการถัดไป และรายงานสาเหตุที่ไม่ได้ลงเวลาปฏิบัติงานต่อผู้บังคับบัญชาทราบด้วยครับ\n\n' \
           'ขอขอบพระคุณที่ท่านร่วมเป็นส่วนหนึ่งกับเรา ในการผ่านวิกฤติ COVID-19 ไปด้วยกัน\n\n' \
           'PEA COVID-19\n' \
           'By PEA Innovation Hub'.format(id)
    m = Message(account=account,
                subject=subject,
                body=body,
                to_recipients=[boss])
    # print('message created')
    m.send_and_save()
    # print(m)
    print('email send: {} >> {}'.format(id, boss))

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
    body = 'ระบบอัตโนมัติ PEA COVID-19 ขอแจ้งให้ทราบว่า\n\n' \
           'ตามที่ท่านได้เข้าร่วมโครงการ Work from home เนื่องจากมีความเสี่ยงในการสัมผัสเชื้อโรค COVID-19 เป็นเวลา 14 วัน ตั้งแต่วันที่ {} ถึงวันที่ {}\n\n' \
           'ทางระบบได้ตรวจสอบพบว่า' \
           'ท่านไม่ได้ทำการติดต่อกับระบบต่อเนื่องเป็นระยะเวลา 3 วัน ตั้งแต่วันที่ {} ถึงวันที่ {}\n\n' \
           'ทีมงาน PEA COVID-19 ห่วงใยสุขภาพของพนักงานทุกคน ระบบต้องการทราบข้อมูลการบันทึกลงเวลาปฏิบัติงาน Time Stamp และข้อมูล Daily Health Update ของท่านทุกวัน\n\n' \
           'ทั้งนี้ระบบได้ทำการรายงานไปยังผู้บังคับบัญชาต้นสังกัดของท่านให้ทราบเรียบร้อยแล้ว\n\n' \
           'ขอให้ท่านทำการบันทึกลงเวลาปฏิบัติงาน Time Stamp และข้อมูล Daily Health Update ในวันทำการถัดไป พร้อมทั้งรายงานสาเหตุที่ไม่ได้ทำการติดต่อกับระบบต่อผู้บังคับบัญชารับทราบด้วยครับ\n\n' \
           'ขอขอบพระคุณที่ท่านร่วมเป็นส่วนหนึ่งกับเรา ในการผ่านวิกฤติ COVID-19 ไปด้วยกัน\n\n' \
           'PEA COVID-19\n' \
           'By PEA Innovation Hub'.format(id)
    m = Message(account=account,
                subject=subject,
                body=body,
                to_recipients=[boss])
    # print('message created')
    m.send_and_save()
    # print(m)
    print('email send: {} >> {}'.format(id, boss))

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
    body = 'ระบบอัตโนมัติ PEA COVID-19 ได้ตรวจสอบพบว่า\n\n' \
           'ตามที่ท่านได้เข้าร่วมโครงการ Work from home เนื่องจากมีความเสี่ยงในการสัมผัสเชื้อโรค COVID-19 เป็นเวลา 14 วัน ตั้งแต่วันที่ {} ถึงวันที่ {} \n\n ' \
           'ท่านไม่ได้ทำการบันทึกเวลาปฏิบัติงาน Time Stamp ในวันที่ {} \n\n' \
           'ทีมงาน PEA COVID-19 ห่วงใยสุขภาพพนักงานทุกท่าน ระบบต้องการทราบข้อมูลการบันทึกเวลาปฏิบัติงาน Time Stamp, ข้อมูล Daily Health Update และ PEA STOP COVID-19 CHALLENGE ของท่านทุกวัน  \n\n' \
           'ขอให้ท่านทำการบันทึกเวลาปฏิบัติงาน Time Stamp, บันทึก Daily Health Update และ PEA STOP COVID-19 CHALLENGE ในวันถัดไป และรายงานสาเหตุที่ไม่ได้ลงเวลาปฏิบัติงานต่อผู้บังคับบัญชารับทราบด้วยครับ \n\n' \
           '* ทั้งนี้หากท่านขาดการติดต่อกับระบบต่อเนื่องเป็นระยะเวลา 3 วัน ระบบจะแจ้งเตือนไปยังผู้บังคับบัญชาต้นสังกัดของท่านต่อไป \n\n' \
           'ขอขอบพระคุณที่ท่านร่วมเป็นส่วนหนึ่งกับเรา ในการผ่านวิกฤติ COVID-19 ไปด้วยกัน \n\n' \
           'PEA COVID-19 \n ' \
           'By PEA Innovation Hub'.format(
        id, day, id, boss, day)


    m = Message(account=account,
                subject=subject,
                body=body,
                to_recipients=[boss])
    # print('message created')
    m.send_and_save()
    # print(m)
    print('email send: {} >> {}'.format(id, boss))


### แจ้งเตือน พนักงาน ขาดการทำ PEA STOP COVID-19 CHALLENGE

def send_email_challenge_warning(request, id, boss, day):
    server = 'email.pea.co.th'
    email = 'peacovid19@pea.co.th'
    username = 'peacovid19'
    password = 'peacovid19'
    boss = boss + '@pea.co.th'
    account = connect(server, email, username, password)
    subject = 'แจ้งเตือน ท่านขาดการเข้าร่วม PEA STOP COVID-19 CHALLENGE'
    body = 'ระบบอัตโนมัติ PEA COVID-19 ขอแจ้งให้ทราบว่า\n\n' \
           'ตามที่ท่านได้เข้าร่วมโครงการ Work from home เนื่องจากมีความเสี่ยงในการสัมผัสเชื้อโรค COVID-19 เป็นเวลา 14 วัน ตั้งแต่วันที่ {} ถึงวันที่ {} \n\n ' \
           'ระบบอัตโนมัติ PEA COVID-19 ได้ตรวจสอบพบว่า' \
           'ท่านไม่ได้ทำการเข้าร่วม PEA STOP COVID-19 CHALLENGE ในวันที่ {} \n\n' \
           'ทีมงาน PEA COVID-19 ห่วงใยสุขภาพพนักงานทุกท่าน ระบบต้องการทราบข้อมูลการบันทึกเวลาปฏิบัติงาน Time Stamp, ข้อมูล Daily Health Update และ PEA STOP COVID-19 CHALLENGE ของท่านทุกวัน  \n\n' \
           'ขอให้ท่านทำการบันทึกเวลาปฏิบัติงาน Time Stamp, บันทึก Daily Health Update และ PEA STOP COVID-19 CHALLENGE ในวันถัดไป และรายงานสาเหตุที่ไม่ได้ลงเวลาปฏิบัติงานต่อผู้บังคับบัญชารับทราบด้วยครับ \n\n' \
           '* ทั้งนี้หากท่านขาดการติดต่อกับระบบต่อเนื่องเป็นระยะเวลา 3 วัน ระบบจะแจ้งเตือนไปยังผู้บังคับบัญชาต้นสังกัดของท่านต่อไป \n\n' \
           'ขอขอบพระคุณที่ท่านร่วมเป็นส่วนหนึ่งกับเรา ในการผ่านวิกฤติ COVID-19 ไปด้วยกัน \n\n' \
           'PEA COVID-19 \n ' \
           'By PEA Innovation Hub'.format(
        id, day, id, boss, day)


    m = Message(account=account,
                subject=subject,
                body=body,
                to_recipients=[boss])
    # print('message created')
    m.send_and_save()
    # print(m)
    print('email send: {} >> {}'.format(id, boss))


### แจ้งเตือน พนักงาน ขาดการทำ Daily Health Update

def send_email_dailyhealth_warning(request, id, boss, day):
    server = 'email.pea.co.th'
    email = 'peacovid19@pea.co.th'
    username = 'peacovid19'
    password = 'peacovid19'
    boss = boss + '@pea.co.th'
    account = connect(server, email, username, password)
    subject = 'แจ้งเตือน ท่านขาดการเข้าร่วม Daily Health Update'
    body = 'ระบบอัตโนมัติ PEA COVID-19 ขอแจ้งให้ทราบว่า\n\n' \
           'ตามที่ท่านได้เข้าร่วมโครงการ Work from home เนื่องจากมีความเสี่ยงในการสัมผัสเชื้อโรค COVID-19 เป็นเวลา 14 วัน ตั้งแต่วันที่ {} ถึงวันที่ {} \n\n ' \
           'ระบบอัตโนมัติ PEA COVID-19 ได้ตรวจสอบพบว่า' \
           'ท่านไม่ได้ทำการบันทึก Daily Health Update ในวันที่ {} \n\n' \
           'ทีมงาน PEA COVID-19 ห่วงใยสุขภาพพนักงานทุกท่าน ระบบต้องการทราบข้อมูลการบันทึกเวลาปฏิบัติงาน Time Stamp, ข้อมูล Daily Health Update และ PEA STOP COVID-19 CHALLENGE ของท่านทุกวัน  \n\n' \
           'ขอให้ท่านทำการบันทึกเวลาปฏิบัติงาน Time Stamp, บันทึก Daily Health Update และ PEA STOP COVID-19 CHALLENGE ในวันถัดไป และรายงานสาเหตุที่ไม่ได้ลงเวลาปฏิบัติงานต่อผู้บังคับบัญชารับทราบด้วยครับ \n\n' \
           '* ทั้งนี้หากท่านขาดการติดต่อกับระบบต่อเนื่องเป็นระยะเวลา 3 วัน ระบบจะแจ้งเตือนไปยังผู้บังคับบัญชาต้นสังกัดของท่านต่อไป \n\n' \
           'ขอขอบพระคุณที่ท่านร่วมเป็นส่วนหนึ่งกับเรา ในการผ่านวิกฤติ COVID-19 ไปด้วยกัน \n\n' \
           'PEA COVID-19 \n ' \
           'By PEA Innovation Hub'.format(
        id, day, id, boss, day)


    m = Message(account=account,
                subject=subject,
                body=body,
                to_recipients=[boss])
    # print('message created')
    m.send_and_save()
    # print(m)
    print('email send: {} >> {}'.format(id, boss))


### แจ้งเตือน พนักงาน ขาดการทำ Time Stamp, PEA STOP COVID-19 CHALLENGE, Daily Health Update

def send_email_activity_warning(request, id, boss, day):
    server = 'email.pea.co.th'
    email = 'peacovid19@pea.co.th'
    username = 'peacovid19'
    password = 'peacovid19'
    boss = boss + '@pea.co.th'
    account = connect(server, email, username, password)
    subject = 'แจ้งเตือน ท่านขาดการติดต่อกับระบบ Work from home'
    body = 'ระบบอัตโนมัติ PEA COVID-19 ขอแจ้งให้ทราบว่า\n\n' \
           'ตามที่ท่านได้เข้าร่วมโครงการ Work from home เนื่องจากมีความเสี่ยงในการสัมผัสเชื้อโรค COVID-19 เป็นเวลา 14 วัน  ตั้งแต่วันที่ {} ถึงวันที่ {} \n\n ' \
           'ระบบอัตโนมัติ PEA COVID-19 ได้ตรวจสอบพบว่า' \
           'ท่านไม่ได้ทำการบันทึกเวลาปฏิบัติงาน Time Stamp, Daily Health Update และ PEA STOP COVID-19 CHALLENGE ในวันที่ {} \n\n' \
           'ทีมงาน PEA COVID-19 ห่วงใยสุขภาพพนักงานทุกท่าน ระบบต้องการทราบข้อมูลการบันทึกเวลาปฏิบัติงาน Time Stamp, ข้อมูล Daily Health Update และ PEA STOP COVID-19 CHALLENGE ของท่านทุกวัน  \n\n' \
           'ขอให้ท่านทำการบันทึกเวลาปฏิบัติงาน Time Stamp, บันทึก Daily Health Update และ PEA STOP COVID-19 CHALLENGE ในวันถัดไป และรายงานสาเหตุที่ไม่ได้ลงเวลาปฏิบัติงานต่อผู้บังคับบัญชารับทราบด้วยครับ \n\n' \
           '* ทั้งนี้หากท่านขาดการติดต่อกับระบบต่อเนื่องเป็นระยะเวลา 3 วัน ระบบจะแจ้งเตือนไปยังผู้บังคับบัญชาต้นสังกัดของท่านต่อไป \n\n' \
           'ขอขอบพระคุณที่ท่านร่วมเป็นส่วนหนึ่งกับเรา ในการผ่านวิกฤติ COVID-19 ไปด้วยกัน \n\n' \
           'PEA COVID-19 \n ' \
           'By PEA Innovation Hub'.format(
        id, day, id, boss, day)


    m = Message(account=account,
                subject=subject,
                body=body,
                to_recipients=[boss])
    # print('message created')
    m.send_and_save()
    # print(m)
    print('email send: {} >> {}'.format(id, boss))
