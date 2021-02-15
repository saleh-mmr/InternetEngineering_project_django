from abc import ABC
from datetime import date
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import *


class MyUser(AbstractUser):
    phone = models.CharField(max_length=50, blank=True)


class Trip(models.Model):
    user_site = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    destination = models.CharField(max_length=50)
    date = models.DateField(default=date.today)
    detail = models.CharField(max_length=300)

    def __str__(self):
        return self.destination


class Participant(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)

    def __str__(self):
        return self.first_name + ' ' + self.last_name


class Transaction(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    payer = models.ForeignKey(Participant, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    fee = models.IntegerField()

    def __str__(self):
        return self.title


class Table(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)

    def __str__(self):
        return self.title


class Bedehkar(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    amount = models.IntegerField()


class Bestankar(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    amount = models.IntegerField()
