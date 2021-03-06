from django.db import models
import json

GENDER_CHOICES = (
    ('male', 'ชาย'),
    ('female', 'หญิง'),
)
BLOOD_CHOICES = (
    ('o', 'โอ'),
    ('a', 'เอ'),
    ('b', 'บี'),
    ('ab', 'เอบี นอร์มอล'),
)
HOSPITAL_CHOICES = (
    ('1month', 'น้อยกว่า 1 เดือน'),
    ('1-2', 'ระหว่าง 1-2 เดือน'),
    ('2month', 'มากกว่า 2 เดือน'),
)

TRUE_FALSE_CHOICES = (
    (True, 'ใช่'),
    (False, 'ไม่ใช่'),

)

ACTIVE_STATUS_CHOICES=(
    ('PEA', 'PEA'),
    ('WFH', 'WFH'),
    ('LEAVE', 'Leave'),
    ('COVID', 'COVID')
)

APPROVED_STATUS = (
    ('Idle', 'Idle'),
    ('WFH', 'WFH'),
    ('LEAVE', 'Leave'),
    ('COVID', 'COVID')
)

HEALTH_STATUS =(
    ('normal', 'ไม่เสี่ยง'),
    ('flu','ไข้หวัด'),
    ('quarantine','แยกตัว'),
    ('hospital', 'พบแพทย์')
)

# Create your models here.
class employee(models.Model):
    emplyee_name=models.CharField(max_length=255)
    employee_ID=models.CharField(max_length=255)
    employee_line_ID = models.CharField(max_length=255)
    activity_text = models.TextField(default='[]')  #
    activity_daily_update = models.TextField(default='[]')
    activity_challenge = models.TextField(default='[]')
    activity_checkin = models.TextField(default='[]')
    activity_checkout = models.TextField(default='[]')

    active_status = models.CharField(max_length=6, choices=ACTIVE_STATUS_CHOICES,blank= True, default='PEA')
    approved_status = models.CharField(max_length=6, choices=APPROVED_STATUS,blank= True, default='Idle')
    WFH_start_date = models.CharField(max_length=255,blank=True)
    WFH_end_date = models.CharField(max_length=255,blank=True)
    LEAVE_start_date =models.CharField(max_length=255,blank=True)
    LEAVE_end_date = models.CharField(max_length=255,blank=True)
    healthy= models.CharField(max_length=255,blank=True, choices=HEALTH_STATUS)
    daily_update=models.BooleanField(default=False)
    challenge=models.BooleanField(default=False)
    quarantined = models.BooleanField(default=False, blank=True)
    infected = models.BooleanField(default=False, blank=True)

    employee_id_up_1 = models.CharField(max_length= 200,blank=True, null=True)
    employee_id_up_2 = models.CharField(max_length= 200,blank=True, null=True)

    employee_age = models.IntegerField (default=0 ,blank= True)
    employee_gender = models.CharField(max_length=6, choices=GENDER_CHOICES,blank= True)
    employee_tel = models.CharField(max_length=10 , blank=True )
    emplyee_address = models.TextField(blank=True )
    emplyee_address14days = models.TextField(blank=True )
    employee_blood = models.CharField(max_length=6, choices=BLOOD_CHOICES,blank= True)
    disease = models.CharField(max_length= 200,blank=True )
    allergic = models.CharField(max_length= 200,blank=True )
    Respiratory_disease =  models.CharField(max_length= 200,blank=True )
    When_respiratory_disease = models.CharField(max_length=20, choices=HOSPITAL_CHOICES,blank= True)
    late_disease = models.CharField(max_length= 200,blank=True )
    late_hospital = models.CharField(max_length= 200,blank=True )
    late_went_to_hospital = models.CharField(max_length=20, choices=HOSPITAL_CHOICES,blank= True)
    hospital = models.CharField(max_length= 200,blank=True )
    work = models.CharField(max_length= 200,blank=True )
    work_tel = models.CharField(max_length=10 , blank=True )
    who_with_you_home = models.CharField(max_length= 200,blank=True )
    relationship = models.CharField(max_length= 200,blank=True )
    who_with_you_home_tel = models.CharField(max_length= 200,blank=True )
    who_with_you_work = models.CharField(max_length= 200,blank=True )
    who_with_you_work_tel = models.CharField(max_length= 200,blank=True )
    emergency_person1 = models.CharField(max_length= 200,blank=True )
    emergency_person1_tel = models.CharField(max_length= 200,blank=True )
    emergency_person2 = models.CharField(max_length= 200,blank=True )
    emergency_person2_tel = models.CharField(max_length= 200,blank=True )
    work_from_home = models.BooleanField (default= False,null=True,blank=True)
    sex = models.CharField(max_length=255, blank=True)
    age = models.CharField(max_length=255, blank=True)
    tel = models.CharField(max_length=255, blank=True)
    work_place = models.CharField(max_length=255, blank=True)
    work_building = models.CharField(max_length=255, blank=True)
    work_floor = models.CharField(max_length=255, blank=True)
    address_no = models.CharField(max_length=255, blank=True)
    address_tumbol = models.CharField(max_length=255, blank=True)
    address_amphur = models.CharField(max_length=255, blank=True)
    address_province = models.CharField(max_length=255, blank=True)
    address_type = models.CharField(max_length=255, blank=True)
    address_to_live = models.CharField(max_length=255, blank=True)
    detention_place = models.CharField(max_length=255, blank=True)
    blood = models.CharField(max_length=255, blank=True)
    congenital_disease_status = models.CharField(max_length=255, blank=True)
    congenital_disease = models.CharField(max_length=255, blank=True)
    drug_allergy_history_status = models.CharField(max_length=255, blank=True)
    drug_allergy_history = models.CharField(max_length=255, blank=True)
    respiratory_disease_status = models.CharField(max_length=255, blank=True)
    respiratory_disease = models.CharField(max_length=255, blank=True)
    last_disease = models.CharField(max_length=255, blank=True)
    last_hospital = models.CharField(max_length=255, blank=True)
    last_time_status = models.CharField(max_length=255, blank=True)
    favorite_hospital = models.CharField(max_length=255, blank=True)
    close_person_first_name = models.CharField(max_length=255, blank=True)
    close_person_last_name = models.CharField(max_length=255, blank=True)
    close_person_tel = models.CharField(max_length=255, blank=True)
    close_person_relationship = models.CharField(max_length=255, blank=True)
    workmate_first_name = models.CharField(max_length=255, blank=True)
    workmate_last_name = models.CharField(max_length=255, blank=True)
    workmate_tel = models.CharField(max_length=255, blank=True)
    workmate_id = models.CharField(max_length=255, blank=True)
    emergency_one_first_name = models.CharField(max_length=255, blank=True)
    emergency_one_last_name = models.CharField(max_length=255, blank=True)
    emergency_one_tel = models.CharField(max_length=255, blank=True)
    emergency_one_relationship=models.CharField(max_length=255, blank=True)
    emergency_two_first_name = models.CharField(max_length=255, blank=True)
    emergency_two_last_name = models.CharField(max_length=255, blank=True)
    emergency_two_tel = models.CharField(max_length=255, blank=True)
    emergency_two_relationship=models.CharField(max_length=255, blank=True)

    employee_posi_text_short=models.CharField(max_length=255, blank=True, null=True)
    employee_dept_sap_short =models.CharField(max_length=255, blank=True, null=True)
    employee_dept_sap=models.CharField(max_length=255, blank=True, null=True)
    employee_dept_upper=models.CharField(max_length=255, blank=True, null=True)
    employee_sub_region=models.CharField(max_length=255, blank=True, null=True)
    employee_emp_email=models.CharField(max_length=255, blank=True, null=True)
    employee_level_code=models.CharField(max_length=255, blank=True, null=True)


    director_approve_name=models.CharField(max_length=255, blank=True, null=True)
    director_approve_id=models.CharField(max_length=255, blank=True, null=True)
    director_approve_email=models.CharField(max_length=255, blank=True, null=True)
    director_approve_position=models.CharField(max_length=255, blank=True, null=True)



    def __str__(self):
        return "{}-{}".format(self.employee_ID, self.emplyee_name)

    # @classmethod
    # def create(cls, emplyee_name, employee_ID, employee_line_ID):
    #     emp = cls(emplyee_name=emplyee_name, employee_ID=employee_ID, employee_line_ID=employee_line_ID)
    #     # do something with the book
    #     return emp

    def last_daily_update(self):
        data = json.loads(self.activity_daily_update)
        return data[-1]['datetime'].split()[0], data[-1]['datetime'].split()[1][1:-1]


class question(models.Model):
    question_text = models.CharField(max_length=200, blank=True)
    answer_1 = models.CharField(max_length=200, blank=True)
    answer_2 = models.CharField(max_length=200, blank=True)
    answer_3 = models.CharField(max_length=200, blank=True)
    correct_answer = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return "{}-{}".format(self.question_text, self.correct_answer)



class emailemployee(models.Model):
    employeeid = models.CharField(max_length=255)
    employeeemail = models.CharField(max_length=255)

    def __str__(self):
        return "{}".format(self.employeeid)



class Director_3_Emails(models.Model):
    position = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    employee_id = models.CharField(max_length=255)
    ref3 = models.CharField(max_length=255)
    ref2 = models.CharField(max_length=255)
    ref1 = models.CharField(max_length=255)
    lastref = models.CharField(max_length=255)
    email = models.CharField(max_length=255)

    def __str__(self):
        return "{}-{}".format(self.employee_id, self.name)



class Director_4_Emails(models.Model):
    position = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    employee_id = models.CharField(max_length=255)
    ref2 = models.CharField(max_length=255)
    ref1 = models.CharField(max_length=255)
    lastref = models.CharField(max_length=255)
    email = models.CharField(max_length=255)

    def __str__(self):
        return "{}-{}".format(self.employee_id, self.name)


class Director_GA_Emails(models.Model):
    position = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    employee_id = models.CharField(max_length=255)
    ref2 = models.CharField(max_length=255)
    ref1 = models.CharField(max_length=255)
    lastref = models.CharField(max_length=255)
    email = models.CharField(max_length=255)

    def __str__(self):
        return "{}-{}".format(self.employee_id, self.name)

class Director_Area_Emails(models.Model):
    position = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    employee_id = models.CharField(max_length=255)
    ref2 = models.CharField(max_length=255)
    ref1 = models.CharField(max_length=255)
    lastref = models.CharField(max_length=255)
    email = models.CharField(max_length=255)

    def __str__(self):
        return "{}-{}".format(self.employee_id, self.name)


class Director_Agency_Emails(models.Model):
    position = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    employee_id = models.CharField(max_length=255)
    ref1 = models.CharField(max_length=255)
    lastref = models.CharField(max_length=255)
    email = models.CharField(max_length=255)

    def __str__(self):
        return "{}-{}".format(self.employee_id, self.name)


class Director_DP_Emails(models.Model):
    position = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    employee_id = models.CharField(max_length=255)
    ref1 = models.CharField(max_length=255)
    lastref = models.CharField(max_length=255)
    email = models.CharField(max_length=255)

    def __str__(self):
        return "{}-{}".format(self.employee_id, self.name)


class Director_Governer_Emails(models.Model):
    position = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    employee_id = models.CharField(max_length=255)
    lastref = models.CharField(max_length=255)
    email = models.CharField(max_length=255)

    def __str__(self):
        return "{}-{}".format(self.employee_id, self.name)
