from django.contrib import admin
from .models import employee, question, emailemployee

# Register your models here.

admin.site.register(employee)
admin.site.register(question)
admin.site.register(emailemployee)

