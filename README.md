# **Crypto Tracker Project**

 ## This  project have two App
- ##   Crypto Tracker App
- ##  Authentication App


## First Install Required Package
```cmd
pip install -r requirments.txt
```

## For migration Run command

```cmd
python manage.py makemigrations
python manage.py migrate
```

## For Create superuser run command run command
```
python manage.py createsuperuser
```

 # **Authentigacatin App**

 - #### Register 
 - #### Cheak mail and verify account
 - #### Now login 
 - #### For password change click on account then password change
 - #### If forget password then click on forget password link then enter register email now You get mail click on link and reset the password
 - #### In this project only loggedin user can see Crypto Currency realtime data


 # **Crypto Tracker App**

 - ## Note:- Celery is not working properly in windos so i use Wsl(Windows Subsystem for Linux) and sqllite database also not working properly so i use Postgresql database

- ## Open a new terminal and run command for celery
```cmd
celery -A crypto_app.celery worker --pool=solo -l info
```
#### OR
```cmd
celery -A crypto_app.celery worker -l info -P eventlet
```
#### OR
```cmd
celery -A crypto_app.celery worker -l info loglevel =info
```

- ## Open a new terminal and run command for celery-beaat
```cmd
celery -A crypto_app beat -l info
```


### Celery-beat run in background and send per min data to django channel group 
### And channel send this data to frontend now we can see real time data of crypto currence that automatically change per miniute



#  **some configuration** 
## detail configuration see code


---



## Configure Settings.py file
```python

INSTALLED_APPS = [
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_celery_results',
    'app',
    'django_celery_beat',
    'auth_app',
]

    
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME':  'ecommerce_project',
        'USER' : 'postgres',
        'PASSWORD':'root',
        'HOST':'localhost',
        'PORT' :'5432'
    }
}


# CELERY SETTINGS

CELERY_BROKER_URL ='redis://127.0.0.1:6379'
CELERY_RESULT_BACKEND = 'django-db'
CELERY_ACCEPT_CONTENT= ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE='Asia/Kolkata'


CELERY_BEAT_SCHEDULER ='django_celery_beat.schedulers:DatabaseScheduler'


CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}



CELERY_IMPORTS = (
    
    
    'app.task',
    
)


from .info import *
EMAIL_USE_TLS =EMAIL_USE_TLS
EMAIL_HOST =EMAIL_HOST
EMAIL_HOST_USER = EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = EMAIL_HOST_PASSWORD
EMAIL_PORT = EMAIL_PORT 
EMAIL_BACKEND= EMAIL_BACKEND



# this data store in info.py
```

## Now configure Celery.py File

```python
from __future__ import absolute_import ,unicode_literals
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE','crypto_app.settings')

app=Celery('crypto_app')


# celery beat settings
app.conf.beat_schedule = {
    'add-every-59-seconds': {
        'task': 'app.task.get_crypto_data',
        'schedule': 59.0,
       
    },
}

app.conf.enable_utc =False
app.conf.update(timezone='Asia/Kolkata')
app.config_from_object(settings,namespace='CELERY')

app.autodiscover_tasks()
@app.task(bind=True)
def debug_task(self):
    print(f'Request : {self.request!r}')

```
## Now configure Task.py file

```python
import asyncio
from .models import Position
from celery import shared_task
import requests
from channels.layers import get_channel_layer

from crypto_app.celery import app
  
@shared_task(bind=True)
def get_crypto_data(self):
    url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=USD&order=market_cap_desc&per_page=100&page=1&sparkline=false"
    data = requests.get(url).json()
    for item in data:
        p,_ = Position.objects.get_or_create(name=item['name'])
        p.image=item['image']
        p.price =item['current_price']
        p.rank=item['market_cap_rank']
        p.market_cap =item['market_cap']
        p.save()        
        # Send Data to Group
        channel_layer= get_channel_layer()
        loop=asyncio.get_event_loop()

        asyncio.set_event_loop(loop)
            
        loop.run_until_complete(channel_layer.group_send("cryptoapp",{
            
                'type':'crypto_update',
                'message': data
            }
            ))
@app.task
def create_test_object():
    get_crypto_data.delay()
```
## Configuration of views.py file

```python

from django.shortcuts import render
import requests
from django.contrib.auth.decorators import login_required




@login_required
def home_view(request):
    url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=USD&order=market_cap_desc&per_page=100&page=1&sparkline=false"
    data = requests.get(url).json()
  
    context ={'data':data,}
    return render (request,'app/index.html',context)

```
# At last views.py file of authentication app

```python
from django.shortcuts import redirect, render  ,HttpResponseRedirect
from django.contrib import messages  
from .forms import CustomUserCreationForm  
from django.contrib.auth import authenticate, login,logout ,update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import PasswordResetForm,SetPasswordForm,PasswordChangeForm
import uuid
from django.core.mail import send_mail
from django.conf import settings
from .models import Verification,ResetPassword
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required



# Create your views here.  

# for sending mail function
def send_mail_after_registration(email,token):
    subject = "Verify your account"
    message = f'Hello  !! \n Welcome to Cropto Lover ! \n  Thank you for visiting Our Website \n We have also send Conformation  Email , Please conform your email address to activate your account. \n\n Thank You \n Ziddi Engineer \n Please click on this link to verify Account \n  http://127.0.0.1:8000/account_verify/{token}'
    from_email = settings.EMAIL_HOST_USER
    recipient_list =[email]
    send_mail(subject=subject ,message=message,from_email=from_email,recipient_list=recipient_list)
    
    
# for password reset mail
def send_mail_for_password_reset(email,token,user):
    subject = f"{user}  ReSet your Password"
    message = f'Hello  !! \n Welcome to Cropto Lover ! \n  Thank you for visiting Our Website \n We have also send Password Reset Email , Please Reset your Password. \n\n Thank You \n Ziddi Engineer \n Please click on this link to Reset Password \n  http://127.0.0.1:8000/password_reset/{token}'
    from_email = settings.EMAIL_HOST_USER
    recipient_list =[email]
    send_mail(subject=subject ,message=message,from_email=from_email,recipient_list=recipient_list)



  # for registraction
def register(request):  
    if request.user.is_authenticated:
        return redirect('/index/')
    
    if request.method == 'POST': 
        
         
        # form = SignupForm(request.POST)  
        form = CustomUserCreationForm(request.POST)  
        if form.is_valid():  
            new_user=form.save() 
            uid= uuid.uuid4()
            pro_obj = Verification(user=new_user,token=uid)
            pro_obj.save()
            send_mail_after_registration(new_user.email,uid)
            messages.success(request,"Your account created Successfully to Verify your account  Cheak your email ")
            return redirect('/login/')
    else:  
        form = CustomUserCreationForm()  
    context = {  
        'form':form  
    }  
    return render(request, 'auth_app/register.html', context)


def account_verify(request,token):
    pf = Verification.objects.filter(token=token).first()
    pf.verify=True
    pf.save()
    messages.success(request, "Your accunt has been  verified , You can login ")
    return redirect('/login/') 




def signin(request):
    
        
    if request.user.is_authenticated:
        return redirect('/index/')
    
    if request.method == "POST":
        
        username= request.POST.get('username')
        pass1= request.POST.get('password')
        user = authenticate(username=username, password=pass1)
        
        
        
        if user is not None:
            pro= Verification.objects.get(user=user)
            if pro.verify:
                login(request,user)
                fname= user.first_name
                return render(request , "auth_app/index.html",{'fname':fname})
                # return redirect('home')  
            else:
                messages.info(request ,"Your account is not verified , please check your mail and verify your Account   !!")
                return redirect("/login/")
            
            
        else:
            form = AuthenticationForm()
            messages.error(request, "Enter Correct Username Or Password !!")
            return render(request,'auth_app/login.html',{'form':form})
    else:
        form = AuthenticationForm()
        return render(request, 'auth_app/login.html', {'form':form})
        


# passwor varification via email

def passwordReset(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            
            if associated_users.exists():
                for user in associated_users:
                    email=user.email
                    uid=uuid.uuid4()
                    user=user
                    token= default_token_generator.make_token(user)
                    # token=uid+tk
                    reset_cheak=ResetPassword.objects.filter(Q(user=user))
                    if reset_cheak.exists():
                        return HttpResponse("Varification mail already sent")
                    else:   
                        password_reset_obj=ResetPassword(user=user,uid=uid,token=token)
                        password_reset_obj.save()
                    try:
                        send_mail_for_password_reset(email,token,user)
                        messages.success(request, "Reset Pssword link send successfully , Cheak your Mail and  Reset the Password ")
                    except Exception as e:
                        return HttpResponse(e)
            # return HttpResponse("Varification mail already sent")
        return redirect("/login/")
    password_reset_form = PasswordResetForm()
    return render(request,'auth_app/password_reset.html',{'form':password_reset_form})


def passwordSet(request,token):
    if request.method=="POST":
        fm =SetPasswordForm(user=request.POST,data=request.POST)
        
        if fm.is_valid():
            password1 = fm.cleaned_data.get("new_password1")
            password2 = fm.cleaned_data.get("new_password2")
        rpass_obj = ResetPassword.objects.get(token=token)
        user=rpass_obj.user
        print(user)
        user.set_password(password1)
        user.save()
        messages.success(request, "Password change successfully, You can login !!!! ")
        return redirect('/login/')
     
    fm=SetPasswordForm(request.user)
    return render(request,'auth_app/password_set.html',{'form':fm})
        
    
   
    
#when old password given
# @login_required
def passwordChange(request):
    if request.user.is_authenticated:
        if request.method=='POST':
            fm =PasswordChangeForm(user=request.user,data=request.POST)
            
            if fm.is_valid():
                fm.save()
                update_session_auth_hash(request,fm.user)
                messages.success(request,"password changed successfully  !!")
                return HttpResponseRedirect('/index/') 
        else:
            fm=PasswordChangeForm(user=request.user)
        return render(request,'auth_app/password_change.html',{'form':fm})
    else:
        return HttpResponseRedirect('/login/')
 
def signout(request):
    logout(request)
    messages.success(request, "LoggedOut successfully")
    return redirect('/login/')


def index(request):
    if not request.user.is_authenticated:
        return redirect('/')
    return render(request,'auth_app/index.html')
        

def home(request):
    return render(request,'auth_app/home.html')
        
```