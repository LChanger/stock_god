# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Create your views here.
from django.contrib.auth.models import User, Group  # 引入model
from rest_framework import viewsets  # 引入viewsets，类似controllers
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse

from stock.serializers import UserSerializer, GroupSerializer  # 引入刚刚定义的序列化器


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

from django.http import HttpResponse
from rest_framework import generics,status,renderers
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from stock.permissions import IsOwnerOrReadOnly
from stock.serializers import *
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
import datetime
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
# 增删改查 stock_info
class StockInfoDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.stock_info.objects.all()
    serializer_class = stock_info_serializer

#统计信息的增删改查(根据id)
class StatisticsViewSet(viewsets.ModelViewSet):
    queryset = models.propensity_statistics.objects.all()
    serializer_class = StatisticsSerializer
    #重写了get_object方法，若传入code和date则根据code和date检索，否则还是调用父类方法按照pk检索
    def get_set(self,code=None,date=None,days=None):
        # if code==None and date==None:
        #     return self.get_object()
        try:
            if days == None:
                if code==None:return models.propensity_statistics.objects.filter(date=date)#查询某一天的所有记录
                elif date==None:return models.propensity_statistics.objects.filter(stock_code=code)#查询某支股票的所有记录
                return models.propensity_statistics.objects.get(stock_code=code, date=date)#查询某一天某支股票统计
            elif date==None:#code 和 days 查询
                return models.propensity_statistics.objects.filter(stock_code=code).order_by('date')[:int(days)]
            return models.propensity_statistics.objects.filter(stock_code=code,
                                                               date__gt=self.get_day_nday_ago(date,days,),
                                                               date__lte=date
                                                               )
        except models.propensity_statistics.DoesNotExist:
            raise Response(status=status.HTTP_400_BAD_REQUEST)
    def list(self, request,*args, **kwargs):
        code = request.GET.get("stock_code")
        date = request.GET.get("date")
        days=request.GET.get("days")
        if code==None and date==None and days==None:
            return super().list(request,*args, **kwargs)
        statistics = self.get_set(code,date,days)
        if days == None and code!=None and date!=None:serializer = StatisticsSerializer(statistics)#若不传入day则只需序列化字典
        else:serializer=self.get_serializer(statistics,many=True)#需要序列化数组
        return Response(serializer.data)

    def get_day_nday_ago(self,date, n):
        t= date.split('-')
        n=int(n)
        y,m,d=int(t[0]),int(t[1]),int(t[2])
        Date = datetime.date(y, m, d) - datetime.timedelta(n)
        return Date
# class StatisticsDetail(APIView,StatisticsViewSet):
#     def update(self, request,*args, **kwargs):
#         code = request.GET.get("stock_code")
#         date = request.GET.get("date")
#         if code==None and date==None:
#             return super().update(request,*args, **kwargs)
#         partial = kwargs.pop('partial', False)
#         instance = self.get_object(code,date)
#         serializer = self.get_serializer(instance, data=request.data, partial=partial)
#         serializer.is_valid(raise_exception=True)
#         self.perform_update(serializer)
#         if getattr(instance, '_prefetched_objects_cache', None):
#             # If 'prefetch_related' has been applied to a queryset, we need to
#             # forcibly invalidate the prefetch cache on the instance.
#             instance._prefetched_objects_cache = {}
#         return Response(serializer.data)
#     def destroy(self, request,*args, **kwargs):
#         code = request.GET.get("stock_code")
#         date = request.GET.get("date")
#         if code==None and date==None:
#             return super().destroy(request,*args, **kwargs)
#         instance = self.get_object(code,date)
#         self.perform_destroy(instance)
#         return Response(status=status.HTTP_204_NO_CONTENT)

# comment 情感分析
class CommentAnalysis(APIView):
    """
    comment annalysis  by rules  and  LSTM
    """
    from stanfordcorenlp import StanfordCoreNLP
    nlp = StanfordCoreNLP(r'F:\Graduationproject\stanford-corenlp-full-2016-10-31', lang='zh')
    from sentiment_analysis import Any
    a = Any.Analysis()
    a.sentiment_init()
    # def __del__(self):
    #     self.nlp.close()
    def post(self, request, format=None):
        comment = request.data.get('comment')
        if comment==None:
            return Response('输入为空', status=status.HTTP_400_BAD_REQUEST)
        pposRules,pnegRules=self.sentiment_by_rules(comment)
        data = {'pposRules': pposRules,
                'pnegRules': pnegRules,
                }
        import json
        payload = json.dumps(data)
        return Response(payload,status=status.HTTP_201_CREATED)
    def sentiment_by_rules(self,comment):
        posscore, negscore=self.a.sentiment_by_rules(self.nlp.word_tokenize(comment), self.nlp.dependency_parse(comment))
        ppos= float(posscore)/ (float(posscore)+ float(negscore))#正向可能性
        pneg=1-ppos#负向可能性
        return ppos,pneg
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
