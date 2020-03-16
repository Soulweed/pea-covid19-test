from django.db import models

# Create your models here.
class employee(models.Model):
    emplyee_name=models.CharField(max_length=255)
    employee_ID=models.IntegerField(default=999999)
    employee_line_ID = models.CharField(max_length=255)
    activity_text = models.TextField(default='000')  #
    quarantined = models.BooleanField(default=False, blank=True, null=True)
    infected = models.BooleanField(default=False, blank=True)


    def __str__(self):
        return "{}".format(self.employee_ID)


    def update_activitiy(self):
        pass

    def form1(self):
        pass


class question(models.Model):
    question_text = models.CharField(max_length=200, blank=True)
    answer_1 = models.CharField(max_length=200, blank=True)
    answer_2 = models.CharField(max_length=200, blank=True)
    answer_3 = models.CharField(max_length=200, blank=True)
    correct_answer = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return "{}".format(self.question_text)