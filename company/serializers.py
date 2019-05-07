
from rest_framework import serializers #引入rest framework的serializers

from company import models
#行业
class industry_serializer(serializers.ModelSerializer):
    class Meta:
        model=models.industry
        fields=('id','name','description')
#关系详情
class relation_info_serializer(serializers.ModelSerializer):
    class Meta:
        model=models.relation_info
        fields=('__all__')

#公司关系
class com_relation_serializer(serializers.ModelSerializer):
    company_one_name=serializers.CharField(source='company_one.com_name',required=False,allow_null=True)
    company_two_name = serializers.CharField(source='company_two.com_name',required=False, allow_null=True)
    class Meta:
        model=models.com_relation
        fields=('__all__')
#公司详情
class company_serializer(serializers.ModelSerializer):
    industry_name=serializers.CharField(source='industry.name',required=False,allow_null=True,allow_blank=True)
    class Meta:
        model=models.company
        fields=('__all__')
        # fields=('id','com_name','com_en_name','stock_code_A','stock_name_A','industry_name','registered_capital','business_regist','introduction','business_scope')
#大宗交易
class block_trade_serializer(serializers.ModelSerializer):
    buyer_name=serializers.CharField(source='buyer.com_name',allow_null=True,allow_blank=True)
    seller_name = serializers.CharField(source='seller.com_name', allow_null=True, allow_blank=True)
    class Meta:
        model=models.block_trade
        fields=('__all__')
#并购重组
class merge_reorganization(serializers.ModelSerializer):
    buyer_name=serializers.CharField(source='buyer.com_name',allow_null=True,allow_blank=True)
    seller_name = serializers.CharField(source='seller.com_name', allow_null=True, allow_blank=True)
    class Meta:
        model=models.block_trade
        fields=('__all__')