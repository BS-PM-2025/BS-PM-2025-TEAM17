from django.urls import path
from . import views
#from this dirctory import views file

urlpatterns=[
    path('',views.dashboard,name='dashboard'),

]