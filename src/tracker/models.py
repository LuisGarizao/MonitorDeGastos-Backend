from uuid import uuid7
from django.db import models
from datetime import datetime
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    email = models.EmailField(unique=True)
    

class ExpenseType(models.TextChoices):
    FOOD = 'food'
    UTILITIES = 'utilities'
    TRANSPORT = 'transport'
    ENTERTAINMENT = 'entertainment'
    HEALTH = 'health'
    OTHER = 'other'

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    type = models.CharField(choices=ExpenseType.choices, default=ExpenseType.OTHER, max_length=20)
    amount = models.IntegerField(null=False)
    date = models.DateTimeField(null=False, default=datetime.now)
    description = models.TextField()
    
