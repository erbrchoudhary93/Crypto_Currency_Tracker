from operator import index
from django.urls import path 
from .import views 


  
  
urlpatterns = [  
     path('',views.register,name='register'),
     path('index/',views.index,name='index'),
     path('login/',views.signin,name='login'),
     path('logout/',views.signout,name='logout'),
     path('home/',views.home,name='home'),
     path('account_verify/<slug:token>',views.account_verify),
     path('password_reset/<slug:token>',views.passwordSet),
     path('preset/',views.passwordReset,name='preset'),
     path('pset/',views.passwordSet,name='pset'),
     path('pchange/',views.passwordChange,name='pchange'),
     
] 