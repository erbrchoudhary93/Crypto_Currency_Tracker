
from django.urls import path 
from .views import home_view 

urlpatterns = [
    path('cryptoindex/',home_view , name='cryptoapp'),
]
