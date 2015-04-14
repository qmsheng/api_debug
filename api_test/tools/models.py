from django.db import models
from django.contrib import admin

# Create your models here.

class modtools(models.Model):
	title = models.CharField(max_length = 150)

# class User(models.Model):
# 	username = models.CharField(max_length=10)

admin.site.register(modtools)

