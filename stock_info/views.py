# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render,HttpResponse
from stock_info import models
# Create your views here.

from django.contrib.auth.models import User, Group #引入model
from rest_framework import viewsets #引入viewsets，类似controllers
from stock_info.serializers import UserSerializer, GroupSerializer,stock_info_serializer#引入刚刚定义的序列化器

# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined') #集合
    serializer_class = UserSerializer  #序列化

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

def index(request):
    return HttpResponse("hello")

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
@csrf_exempt
def stock_info_list(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        stock_infos = models.stock_info.objects.all()
        serializer = stock_info_serializer(stock_infos, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = stock_info_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)
@csrf_exempt
def stock_info_detail(request, pk):
    """
    Retrieve, update or delete a code snippet.
    """
    try:
        snippet = models.stock_info.objects.get(pk=pk)
    except models.stock_info.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = stock_info_serializer(snippet)
        return JsonResponse(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = stock_info_serializer(snippet, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        snippet.delete()
        return HttpResponse(status=204)

def add_stock_info(request):
    if request.method=='POST':
        serializer = stock_info_serializer(data=request.body)
        # 2.需要调用序列化器的 is_valid 方法 valid验证  返回True False
        # 如果数据可用  返回True
        serializer.is_valid()
        # raise_exception=True 可以设置为True 来抛出异常
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # id=request.POST.get("stock_code",None)
        # name=request.POST.get("stock_name",None)
        # stock=models.stock_info(stock_id=id,stock_name=name)
        # stock.save()
        return HttpResponse("<p>数据添加成功！</p>")
