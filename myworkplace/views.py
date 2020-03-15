from django.shortcuts import render
from .models import employee
# Create your views here.
def home(request):
    data1 = employee.objects.all()

    context = {'number_of_employee': len(data1)}
    print(context)
    return render(request, 'applicant/home.html', context)
