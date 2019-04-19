# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
# Create your models here.
class stock_info(models.Model):
    stock_id=models.CharField(primary_key=True,max_length=6,null=False,unique=True)
    stock_name = models.CharField(max_length=20,null=False,unique=True)
    theme_id= models.CharField(max_length=20,null=True)
    theme_name = models.CharField(max_length=20,null=True)
    description = models.TextField(null=True)

    def __str__(self):
        return '[{}] {} ({})'.format(self.stock_id, self.stock_name)
    class Meta:
        ordering = ('stock_id',)

class Customer(models.Model):
    username = models.CharField(max_length=20,null=False)
    password = models.CharField(max_length=20,null=False)
    sex=models.IntegerField()#0-男，1-女
    user_phone=models.CharField(max_length=20,null=False)
    gmt_create=models.DateField(auto_now_add=True)
    gmt_modified=models.DateField(auto_now=True)

class Selection(models.Model):
    stock_code = models.CharField(max_length=6)
    owner = models.CharField(max_length=20,null=False)  # 所属用户
    gmt_create = models.DateField(auto_now_add=True)
    def __str__(self):
        return '()'.format(self.stock_code, self.owner)

class propensity_statistics(models.Model):
    stock_code = models.CharField(max_length=6)
    date= models.DateField()
    total_posts=models.IntegerField()
    bullish_num=models.IntegerField()
    bearish_num=models.IntegerField()
    neutral_num=models.IntegerField()
    storage_location=models.CharField(max_length=100)
    description = models.TextField(null=True)
    def __str__(self):
        return '()'.format(self.stock_code, self.date)
    class Meta:
        unique_together = ("stock_code", "date")