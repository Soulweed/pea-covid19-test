from django.contrib import admin
from .models import employee, question, emailemployee, Director_4_Emails, Director_3_Emails, \
    Director_Area_Emails, Director_GA_Emails, Director_Agency_Emails, Director_Governer_Emails, Director_DP_Emails

# Register your models here.

admin.site.register(employee)
admin.site.register(question)
admin.site.register(Director_4_Emails)
admin.site.register(Director_3_Emails)
admin.site.register(Director_Area_Emails)
admin.site.register(Director_GA_Emails)
admin.site.register(Director_Agency_Emails)
admin.site.register(Director_DP_Emails)
admin.site.register(Director_Governer_Emails)

