from django.contrib import admin
from .models import employee, question, emailemployee, Director_4_Emails, Director_3_Emails

# Register your models here.

admin.site.register(employee)
admin.site.register(question)
admin.site.register(Director_4_Emails)
admin.site.register(Director_3_Emails)


