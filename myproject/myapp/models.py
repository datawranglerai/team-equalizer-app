from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Votes(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    player = models.CharField(max_length=200)
    attack = models.IntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(10)])
    defense = models.IntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(10)])
    possession = models.IntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(10)])
    stamina = models.IntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(10)])
    mobility = models.IntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(10)])
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.title


class Roster(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    published_date = models.DateTimeField(blank=True, null=True)
    players = models.CharField(max_length=1000)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.title
