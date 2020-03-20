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


# Create your models here.
class employee(models.Model):
    emplyee_name=models.CharField(max_length=255)
    employee_ID=models.CharField(max_length=255)
    employee_line_ID = models.CharField(max_length=255)
    activity_text = models.TextField(default='000')  #
    quarantined = models.BooleanField(default=False, blank=True)
    infected = models.BooleanField(default=False, blank=True)
    healthy= models.CharField(max_length=255)


    employee_id_up_1 = models.CharField(max_length= 200,blank=True )
    employee_id_up_2 = models.CharField(max_length= 200,blank=True )

    employee_age = models.IntegerField (default=0 ,blank= True)
    employee_gender = models.CharField(max_length=6, choices=GENDER_CHOICES,blank= True)
    employee_tel = models.CharField(max_length=10 , blank=True )
    # employee_line = models.CharField(max_length= 200,blank=True )
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
    # explain_7days_ago = models.TextField(blank=True )
    work_from_home = models.BooleanField (default= False,null=True,blank=True)
    # Quarantine = models.BooleanField (default= False,null=True,blank=True)
    # Infect = models.BooleanField (default= False,null=True,blank=True)

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
    emergency_one_first_name = models.CharField(max_length=255, blank=True)
    emergency_one_last_name = models.CharField(max_length=255, blank=True)
    emergency_one_tel = models.CharField(max_length=255, blank=True)
    emergency_two_first_name = models.CharField(max_length=255, blank=True)
    emergency_two_last_name = models.CharField(max_length=255, blank=True)
    emergency_two_tel = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return "{}".format(self.employee_ID)

class question(models.Model):
    question_text = models.CharField(max_length=200, blank=True)
    answer_1 = models.CharField(max_length=200, blank=True)
    answer_2 = models.CharField(max_length=200, blank=True)
    answer_3 = models.CharField(max_length=200, blank=True)
    correct_answer = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return "{}-{}".format(self.question_text, self.correct_answer)


