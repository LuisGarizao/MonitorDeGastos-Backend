from uuid import uuid7
from django.db import models
from datetime import date
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

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
    amount = models.IntegerField(null=False, validators=[MinValueValidator(0)])
    date = models.DateField(null=False, default=date.today, validators=[MaxValueValidator(date.today)])
    description = models.TextField(blank=True, default="")
    
