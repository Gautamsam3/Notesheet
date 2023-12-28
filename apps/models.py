from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class profile (models.Model):
  user = models.OneToOneField(User, null=True, on_delete = models.CASCADE)
  designation= models.CharField(max_length=100, blank=True)
  department = models.CharField(max_length=100, blank=True)
  faculty =  models.CharField(max_length=100, blank=True)
  def __str__(self):
    return str(self.designation)

  def __str__(self):
    return str(self.department)

  def __str__(self):
    return str(self.faculty)
  
class notesheet(models.Model):
    name = models.CharField(max_length=255)
    faculty = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    event_name = models.CharField(max_length=255)
    event_date = models.DateField()
    event_time = models.TimeField()
    intro = models.TextField()
    objective = models.TextField()
    brief_desc = models.TextField()
    reg_fee =  models.CharField(max_length=255,default="NA")
    brochure = models.ImageField(upload_to='brochures/',default="NA")
    channels = models.ManyToManyField(User, related_name='channels')
    current_reviewer = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)


class Review(models.Model):
    Notesheet = models.ForeignKey(notesheet, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')],default="Pending")
    comment = models.TextField(null=True, blank=True)
