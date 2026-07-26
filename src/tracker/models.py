from uuid import uuid7
from django.db import models
from datetime import datetime
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    email = models.EmailField(unique=True)
    

class PlanStatus(models.TextChoices):
    PENDING = 'pending'
    ONGOING = 'ongoing'
    COMPLETED = 'completed'
    DISCARDED = 'discarded'

class Plan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    status = models.CharField(choices=PlanStatus.choices, default=PlanStatus.ONGOING, max_length=15)
    expense_limit = models.IntegerField(null=False)
    start_date = models.DateField(null=False)
    end_date = models.DateField(null=False)
    

class ExpenseType(models.TextChoices):
    FOOD = 'food'
    UTILITIES = 'utilities'
    TRANSPORT = 'transport'
    ENTERTAINMENT = 'entertainment'
    HEALTH = 'health'
    OTHER = 'other'

class Expense(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    type = models.CharField(choices=ExpenseType.choices, default=ExpenseType.OTHER, max_length=20)
    amount = models.IntegerField(null=False)
    date = models.DateTimeField(null=False, default=datetime.now)
    description = models.TextField()
    
