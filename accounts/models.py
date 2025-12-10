from django.db import models
from django.contrib.auth.models import User

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.CharField(max_length=50)
    image = models.CharField(max_length=200) # Path to static image
    duration = models.CharField(max_length=50)
    instructor = models.CharField(max_length=100)
    rating = models.FloatField(default=0.0)
    reviews = models.IntegerField(default=0)
    video_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title

class Student(models.Model):
    fullname = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    is_admin = models.BooleanField(default=False)
    enrolled_courses = models.ManyToManyField(Course, blank=True)
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.fullname
    

    

# Create your models here.
