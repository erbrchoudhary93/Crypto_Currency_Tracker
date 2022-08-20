
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Verification(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    token=  models.CharField(max_length=150)
    verify= models.BooleanField(default=False)
    
class ResetPassword(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    token=  models.CharField(max_length=150)
    uid=  models.CharField(max_length=150)
  
    
   
