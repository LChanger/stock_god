# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
# Create your models here.
class stock_info(models.Model):
    stock_id=models.IntegerField()
    stock_name = models.CharField(max_length=20)
    theme_id= models.CharField(max_length=20)
    theme_name = models.CharField(max_length=20)
    description = models.TextField()

    def __str__(self):
        return '[{}] {} ({})'.format(self.stock_id, self.stock_name)
    class Meta:
        ordering = ('stock_id',)


