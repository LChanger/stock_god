
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
    company_main_name=serializers.CharField(source='company_main.com_name', allow_null=True, allow_blank=True)
    class Meta:
        model=models.block_trade
        fields=('__all__')
#并购重组
class merge_reorganization_serializer(serializers.ModelSerializer):
    company_main_name=serializers.CharField(source='company_main.com_name', allow_null=True, allow_blank=True)
    buyer_name=serializers.CharField(source='buyer.com_name',allow_null=True,allow_blank=True)
    seller_name = serializers.CharField(source='seller.com_name', allow_null=True, allow_blank=True)
    target_name = serializers.CharField(source='transaction_target.com_name', allow_null=True, allow_blank=True)
    class Meta:
        model=models.merge_reorganization
        fields=('__all__')
#重大合同
class major_contract_serializer(serializers.ModelSerializer):
    company_main_name=serializers.CharField(source='company_main.com_name', allow_null=True, allow_blank=True)
    signing_body_name = serializers.CharField(source='signing_body.com_name', allow_null=True, allow_blank=True)
    body_relation_name = serializers.CharField(source='body_relation.name', allow_null=True, allow_blank=True)
    signing_others_name = serializers.CharField(source='signing_others.com_name', allow_null=True, allow_blank=True)
    others_relation_name = serializers.CharField(source='others_relation.name', allow_null=True, allow_blank=True)
    class Meta:
        model=models.major_contract
        fields=('__all__')
        # extra_kwargs = {
        #     'body_relation': {'read_only': True},
        #     'contract_amount':{'allow_bank':True},
        #     'income_rate': {'allow_bank': True},
        #     'up_and_down': {'allow_bank': True},
        #     'company_main_id':{'require':False}
        # }
#长期期权投资
class option_invest_serializer(serializers.ModelSerializer):
    invest_com_name=serializers.CharField(source='invest_com.com_name', allow_null=True, allow_blank=True,required=False)
    company_main_name = serializers.CharField(source='company_main.com_name', allow_null=True, allow_blank=True,
                                            required=False)
    class Meta:
        model=models.option_invest
        fields=('__all__')
#关联交易
class related_transaction_serializer(serializers.ModelSerializer):
    company_main_name = serializers.CharField(source='company_main.com_name', allow_null=True, allow_blank=True,
                                              required=False)
    transaction_com_name = serializers.CharField(source='transaction_com.com_name', allow_null=True, allow_blank=True,
                                              required=False)
    class Meta:
        model=models.related_transaction
        fields=('__all__')
#十大流通股东
class cir_shareholder_serializer(serializers.ModelSerializer):
    company_main_name = serializers.CharField(source='company_main.com_name', allow_null=True, allow_blank=True,
                                              required=False)
    shareholder_name = serializers.CharField(source='shareholder.com_name', allow_null=True, allow_blank=True,
                                              required=False)
    class Meta:
        model=models.cir_shareholder
        fields=('__all__')


#人员列表
class person_serializer(serializers.ModelSerializer):
    # company_set = serializers.PrimaryKeyRelatedField(label='关联公司',queryset=models.company.objects.all(),required=False,many=True)
    # affiliated_com_name= com_per_serializer(read_only=True,many=True,label='外键')
    affiliated_com = serializers.StringRelatedField(many=True,read_only=True)
    class Meta:
        model=models.person
        fields=('__all__')
#人员公司关联列表
class com_per_serializer(serializers.ModelSerializer):
    person_name=person_serializer(many=False, read_only=True)
    com_name=serializers.CharField(source='company.com_name', allow_null=True, allow_blank=True,
                                              required=False)
    class Meta:
        model=models.com_per
        # fields=('person_name,com_name,post,app_time')
        fields = ('__all__')
