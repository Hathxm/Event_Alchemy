from django.db import models
from django.contrib.auth.models import AbstractUser
from managers.models import AllUsers,venues,Managers
from vendors.models import vendorservices 
from superadmin.models import Events

# Create your models here.

class Customusers(AllUsers):
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

class Booking(models.Model):
    customer = models.ForeignKey(Customusers, on_delete=models.CASCADE)
    venue = models.ForeignKey(venues, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    Total = models.BigIntegerField()
    services = models.ManyToManyField(vendorservices,blank=True)
    manager = models.ForeignKey(Managers, on_delete=models.CASCADE)
    event_type = models.ForeignKey(Events, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.venue} booking on {self.date} from {self.start_time} to {self.end_time}'
        
    
  
    



