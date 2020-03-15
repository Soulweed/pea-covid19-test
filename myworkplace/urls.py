from django.urls import path
from myworkplace.views import home
app_name = 'myworkplace'

urlpatterns = [
    path('', home, name='home'),

]
