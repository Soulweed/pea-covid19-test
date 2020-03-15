from django.db import models

# Create your models here.
class employee(models.Model):
    emplyee_name=models.CharField(max_length=300)
    employee_ID=models.IntegerField(default=999999)
    activity_text = models.TextField(max_length=300, default='000')  #


    def __str__(self):
        return "{}".format(self.employee_ID)


    def update_activitiy(self):
        pass
