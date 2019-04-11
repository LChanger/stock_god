# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# Create your views here.
from django.contrib.auth.models import User, Group #引入model
from rest_framework import viewsets #引入viewsets，类似controllers
from stock.serializers import UserSerializer, GroupSerializer,stock_info_serializer#引入刚刚定义的序列化器
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'users': reverse('user-list', request=request, format=format),
        'stocks': reverse('stock-list', request=request, format=format)
    })
# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined') #集合
    serializer_class = UserSerializer  #序列化

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework import generics,status,renderers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from stock.permissions import IsOwnerOrReadOnly
from stock.serializers import *
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
#用于登录
class UserLoginAPIView(APIView):
    queryset = models.Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = (AllowAny,)

    def post(self, request, format=None) :
        data = request.data
        username = data.get('username')
        password = data.get('password')
        user =models.Customer.objects.get(username__exact=username)
        if user.password == password:
            serializer = CustomerSerializer(user)
            new_data = serializer.data
            # 记忆已登录用户
            self.request.session['user_id'] = user.id
            return Response(new_data, status=HTTP_200_OK)
        return Response('password error', HTTP_400_BAD_REQUEST)

#用于注册
class UserRegisterAPIView(APIView):
    queryset = User.objects.all()
    serializer_class = CustomerRegisterSerializer
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        data = request.data
        username = data.get('username')
        user_phone=data.get('user_phone')
        if models.Customer.objects.filter(username__exact=username) or models.Customer.objects.filter(user_phone__exact=user_phone)  :
            return Response("用户名已存在",HTTP_400_BAD_REQUEST)
        serializer = CustomerRegisterSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data,status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

#用于用户选股的增删改查  除了查看，其他都需要权限
class SelectionViewSet(viewsets.ModelViewSet):
    queryset = models.Selection.objects.all()
    serializer_class = SelectionSerializer
    permission_classes = (IsOwnerOrReadOnly,)

    def create(self, request, *args, **kwargs):
        data=request.data
        if models.Selection.objects.filter(owner=models.Customer.objects.get(id=self.request.session.get('user_id')).username,stock_code=data.get("stock_code")):
            return Response("该股已关注", HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        print(self.request.user)
        serializer.save(owner=models.Customer.objects.get(id=self.request.session.get('user_id')).username)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

#用户的增删改查
class CustomerViewSet(viewsets.ModelViewSet):
    queryset = models.Customer.objects.all()
    serializer_class = UserSerializer


class StockHighlight(generics.GenericAPIView):
    queryset = models.stock_info.objects.all()
    renderer_classes = (renderers.StaticHTMLRenderer,)

    def get(self, request, *args, **kwargs):
        stock = self.get_object()
        return Response(stock.highlighted)
#list和create stock_info
class StockInfoList(generics.ListCreateAPIView):
    queryset = models.stock_info.objects.all()
    serializer_class =stock_info_serializer
    # # @csrf_exempt
    def post(self, request, *args, **kwargs):
        if isinstance(request.data,dict):
            return super().post(request, *args, **kwargs)
        datas = request.data
        for data in datas:
            serializer = stock_info_serializer(data=data)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(datas)
# 增删改查
class StockInfoDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.stock_info.objects.all()
    serializer_class = stock_info_serializer
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
    elif request.method=='PATCH':
        datas = JSONParser().parse(request)
        for data in datas:
            serializer = stock_info_serializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

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
        # stock=models.stock(stock_id=id,stock_name=name)
        # stock.save()
        return HttpResponse("<p>数据添加成功！</p>")
