from django.shortcuts import render
from rest_framework import viewsets
from company import models
from company.serializers import industry_serializer,company_serializer,relation_info_serializer,block_trade_serializer,com_relation_serializer
from rest_framework import generics,request,status
from rest_framework.response import Response
# Create your views here.
#行业的增删改查
class IndustryViewSet(viewsets.ModelViewSet):
    queryset = models.industry.objects.all()
    serializer_class =industry_serializer
#关系详情的增删改查
class RelationInfoViewSet(viewsets.ModelViewSet):
    queryset = models.relation_info.objects.all()
    serializer_class =relation_info_serializer
    lookup_field =  'name'


#公司之间关系的增删改查
class ComRelationViewSet(viewsets.ModelViewSet):
    queryset = models.com_relation.objects.all()
    serializer_class =com_relation_serializer
    # lookup_field =  'name'
    def create(self, request, *args, **kwargs):
        data = request.data
        try:
            com1 = models.company.objects.get(com_name=data["com_one"])
        except Exception as e:
            return Response("company_main not exsit", status=status.HTTP_400_BAD_REQUEST)
        try:
            com2 = models.company.objects.get(com_name=data["com_two"])
        except Exception as e:
            return Response("company_main not exsit", status=status.HTTP_400_BAD_REQUEST)
        try:
            rel = models.com_relation.objects.get(company_one=com1.id,company_two=com2.id)
        except Exception as e:
            return Response("relation is not exsit", status=status.HTTP_400_BAD_REQUEST)
        serializer=com_relation_serializer(rel)
        #TODO 由tablename 自动查询表信息
        return Response(serializer.data, status=status.HTTP_200_OK)

#公司的list和post
class CompanyList(generics.ListCreateAPIView):
    queryset = models.company.objects.all()
    serializer_class = company_serializer
    def post(self, request, *args, **kwargs):
        data = request.data
        industry=self.generate_industry(data["industry"])#若无此行业则创建行业
        data['industry']=industry.id
        data['industry_name']=industry.name
        #如果存在该公司名，则直接更新
        try:
            com = models.company.objects.get(com_name=data["name"])
        except Exception as e:
            com = None
        if com==None:
            serializer = company_serializer(data=data)
        else:serializer=company_serializer(com,data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            self.IndustryCheck(industry.id,data["com_name"])#生成同一行业关系
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #若无此行业则创建行业
    def generate_industry(self,industry_name):
        try:
            industry = models.industry.objects.get(name=industry_name)
        except Exception as e:
            industry = None
        if industry==None:
            data={}
            data["name"]=industry_name
            serializer = company_serializer(data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                industry = models.industry.objects.get(name=industry_name)
        return industry
    #生成同一行业关系
    def IndustryCheck(self,industry,company):
        companys=models.company.objects.filter(industry_id=industry)
        comone = models.company.objects.get(com_name=company)
        for comtwo in companys:
            rel_data = {}
            rel_data["company_one"] =comone.id
            rel_data["company_two"] =comtwo.id
            if comone.id==comtwo.id:continue
            relation_info = models.relation_info.objects.get(name="同一行业")
            rel_data["relation_name"] = relation_info.name
            rel_data["table_name"] = relation_info.table_name
            relation_serializer = com_relation_serializer(data=rel_data)
            if relation_serializer.is_valid(raise_exception=True):
                relation_serializer.save()
            else:
                return Response(relation_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return True

class CompanyDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.company.objects.all()
    serializer_class = company_serializer
#大宗交易的list和post
class BlockTradeList(generics.ListCreateAPIView):
    queryset = models.block_trade.objects.all()
    serializer_class = block_trade_serializer
    def post(self, request, *args, **kwargs):
        data = request.data
        try:
            buyer = models.company.objects.get(com_name=data["buyer"])
        except Exception as e:
            buyer = None
        #如果不存在买方公司，先在company表中创建买方公司
        if buyer==None:
            com_data={}
            com_data["com_name"]=data["buyer"]
            comserializer = company_serializer(data=com_data)
            if comserializer.is_valid(raise_exception=True):
                comserializer.save()
            buyer=models.company.objects.get(com_name=data["buyer"])
        data['buyer'] = buyer.id
        data['buyer_name'] = buyer.com_name
        #如果不存在卖方公司，先在company表中创建卖方公司
        try:
            seller = models.company.objects.get(com_name=data["seller"])
        except Exception as e:
            seller = None
        if seller == None:
            com_data = {}
            com_data["com_name"] = data["seller"]
            comserializer = company_serializer(data=com_data)
            if comserializer.is_valid(raise_exception=True):
                comserializer.save()
                seller = models.company.objects.get(com_name=data["seller"])
        data['seller'] = seller.id
        data['seller_name'] = seller.com_name
        try:
            company_main = models.company.objects.get(com_name=data["company_main"])
            data["company_main"]=company_main.id
        except Exception as e:
            return Response("company_main not exsit", status=status.HTTP_400_BAD_REQUEST)
        serializer = block_trade_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            # serializer.save()
            #向关系表中插入数据
            rel_data = {}
            rel_data["company_one"] = buyer.id
            rel_data["company_two"] = seller.id
            relation_info=models.relation_info.objects.get(name="大宗交易")
            rel_data["relation_name"]=relation_info.name
            rel_data["table_name"]=relation_info.table_name
            relation_serializer=com_relation_serializer(data=rel_data)
            if relation_serializer.is_valid(raise_exception=True):
                relation_serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)