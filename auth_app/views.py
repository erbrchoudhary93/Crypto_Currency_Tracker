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
    

    # form = PasswordChangeForm()
    # return render(request,'auth_app/password_change.html',{'form':form})




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
        