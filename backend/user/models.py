from django.db import models
from django.contrib.auth.models import AbstractUser
from managers.models import AllUsers

# Create your models here.

class Customusers(AllUsers):
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        
    
  
    



