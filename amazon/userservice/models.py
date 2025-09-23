from django.db import models
from django.contrib.auth.models import *
    
class User(AbstractUser):
    phonenumber = models.CharField(max_length=30)
    

    class Meta:
        db_table = "user_custom"
        verbose_name = "User"