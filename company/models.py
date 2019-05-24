# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
# Create your models here.
#行业表
class industry(models.Model):
    name=models.CharField(max_length=20,null=False,unique=True)
    description = models.TextField(null=True)
    class Meta:
        db_table='industry'
#公司关系详情表
class relation_info(models.Model):
    name=models.CharField(max_length=20,unique=True)#关系名
    table_name=models.CharField(max_length=50,null=True)#表名
    description = models.TextField(null=True)
    class Meta:
        db_table='relation_info'
#人员表
class person(models.Model):
    name=models.CharField(max_length=20,null=False)
    ages=models.IntegerField(null=True,blank=True)
    edu_background=models.CharField(max_length=20,null=True,blank=True)#学历
    introduction=models.TextField(null=True,blank=True)#简介
    affiliated_com=models.ManyToManyField('company',through='com_per')#关联公司
#人员与公司关联表
class com_per(models.Model):
    person=models.ForeignKey('person',on_delete=models.CASCADE,db_constraint=False,related_name='perofcom')
    company=models.ForeignKey('company',on_delete=models.CASCADE,db_constraint=False)
    post=models.CharField(max_length=20,null=True,blank=True)#职位
    app_time=models.DateField(null=True)#任职时间

    def __str__(self):
        return '职务：%s \n 任职时间：%s' % (self.post, self.app_time)

#公司表
class company(models.Model):
    com_name = models.CharField(max_length=100,null=False,unique=True)
    com_en_name=models.CharField(max_length=100,null=True,unique=True)
    stock_code_A=models.CharField(max_length=20,null=True,unique=True)#A股代码
    stock_name_A=models.CharField(max_length=20,null=True,unique=True)#A股简称
    stock_code_B=models.CharField(max_length=20,null=True,unique=True)#B股代码
    stock_name_B=models.CharField(max_length=20,null=True,unique=True)#B股简称
    stock_code_H=models.CharField(max_length=20,null=True,unique=True)#H股代码
    stock_name_H=models.CharField(max_length=20,null=True,unique=True)#H股简称
    industry=models.ForeignKey(industry,on_delete=models.PROTECT,db_constraint=False,null=True,)#所属行业
    registered_capital=models.CharField(max_length=20,null=True,)
    business_regist=models.CharField(max_length=18,null=True,)#工商登记
    introduction = models.TextField(null=True)  # 简介
    business_scope=models.TextField(null=True)  # 经营范围
    class Meta:
        db_table='company'
    def __str__(self):
        return '%s' % (self.com_name)
# 大宗交易
class block_trade(models.Model):
    company_main = models.ForeignKey(company, on_delete=models.CASCADE, related_name='trade_company',
                                     db_constraint=False)  # 公司
    transaction_time=models.DateField(null=True)#交易日期
    up_and_down=models.CharField(max_length=20,null=True,blank=True) #涨跌幅（百分比）
    closing_price=models.CharField(max_length=20,null=True,blank=True) #收盘价（元）
    transaction_price=models.CharField(max_length=20,null=True,blank=True) #成交价（元）
    folding_rate=models.CharField(max_length=20,null=True,blank=True) #折溢率（百分数）
    volume=models.CharField(max_length=20,null=True,blank=True) #成交量 （万股）
    turnover=models.CharField(max_length=20,null=True,blank=True) #成交额（万元）
    turnover_divide_market=models.CharField(max_length=20,null=True,blank=True) #成交额/流通市值(%)
    buyer=models.ForeignKey(company,on_delete=models.CASCADE,related_name='trade_buyer',db_constraint=False)
    seller=models.ForeignKey(company,on_delete=models.CASCADE,related_name='trade_seller',db_constraint=False)
    class Meta:
        db_table='block_trade'
#并购重组
class merge_reorganization(models.Model):
    company_main=models.ForeignKey(company,on_delete=models.CASCADE,related_name='merge_company',db_constraint=False)
    transaction_target=models.ForeignKey(company,on_delete=models.CASCADE,related_name='transaction_target',db_constraint=False)#交易标的
    buyer=models.ForeignKey(company,on_delete=models.CASCADE,related_name='merge_buyer',db_constraint=False)
    seller=models.ForeignKey(company,on_delete=models.CASCADE,related_name='merge_seller',db_constraint=False)
    turnover = models.CharField(max_length=20,null=True,blank=True)  # 交易额（元）
    currency= models.CharField(max_length=20,null=True,blank=True)#币种
    target_type=models.CharField(max_length=20,null=True,blank=True)#标的类型
    transfer_rate=models.FloatField(null=True,blank=True)#股权转让比例(%)
    notice_date=models.DateField()#最新公告日期
    class Meta:
        db_table='merge_reorganization'
#重大合同
class major_contract(models.Model):
    name=models.CharField(max_length=20,null=True)#合同名称
    company_main = models.ForeignKey(company, on_delete=models.CASCADE, related_name='contract_company',
                                     db_constraint=False,null=True)#公司
    signing_body=models.ForeignKey(company, on_delete=models.CASCADE,related_name='signing_body',db_constraint=False,null=True)#签署主体
    body_relation=models.ForeignKey(relation_info, on_delete=models.CASCADE,related_name='body_relation',db_constraint=False,null=True)#签署主体与上市公司的关系
    signing_others=models.ForeignKey(company, on_delete=models.CASCADE,related_name='signing_others',db_constraint=False,null=True)#其他签署方
    others_relation = models.ForeignKey(relation_info, on_delete=models.CASCADE,related_name='others_relation',db_constraint=False,null=True)#其他签署方与上市公司的关系
    contract_type=models.CharField(max_length=20,null=True,blank=True)#合同类型
    contract_amount=models.CharField(max_length=20,null=True,blank=True)#合同金额(元）
    income_rate=models.FloatField(max_length=100,null=True,blank=True)#占上年度营业收入比例(%)
    up_and_down = models.FloatField(max_length=100,null=True,blank=True)#公告后20日涨跌幅(%)
    update_date=models.DateField()#更新时间
    class Meta:
        db_table='major_contract'
#长期期权投资
class option_invest(models.Model):
    company_main = models.ForeignKey(company, on_delete=models.CASCADE,related_name='invest_company',db_constraint=False)#公司
    invest_com= models.ForeignKey(company, on_delete=models.CASCADE,related_name='invest_com',db_constraint=False)#投资公司名称
    hold_stock=models.CharField(max_length=20,null=True,blank=True)#持股数量（股）
    initial_balance=models.CharField(max_length=20,null=True,blank=True)#期初余额(元)
    report_loss=models.CharField(max_length=20,null=True,blank=True)#报告期损益(元）
    end_value=models.CharField(max_length=20,null=True,blank=True)#期末账面价值(元)
    percentage_invest= models.CharField(max_length=20,null=True,blank=True)#占长期股权投资总额比例(%)
    percentage_com= models.CharField(max_length=20,null=True,blank=True)#占该公司股权比例(%)
    invest_com_type=models.CharField(max_length=20,null=True,blank=True)#投资公司类型
    notice_date=models.DateField()#公告日期
    class Meta:
        db_table='option_invest'
#关联交易表
class related_transaction(models.Model):
    company_main = models.ForeignKey(company,on_delete=models.CASCADE,related_name='related_company', db_constraint=False)#公司
    transaction_com=models.ForeignKey(company, on_delete=models.CASCADE,related_name='transaction_com',db_constraint=False)#交易方
    related_type=models.CharField(max_length=20,null=True,blank=True)#关联关系
    turnover = models.CharField(max_length=20,null=True,blank=True)  # 交易额（元）
    currency= models.CharField(max_length=20,null=True,blank=True)#币种
    transaction_mode=models.CharField(max_length=20,null=True,blank=True)#交易方式
    is_control=models.CharField(max_length=1,null=True,blank=True)#是否存在控制关系0-否，1-是
    notic_date=models.DateField()#公告日期
    class Meta:
        db_table='related_transaction'

#十大流通股东表
class cir_shareholder(models.Model):
    company_main = models.ForeignKey(company,on_delete=models.CASCADE,related_name='cir_company', db_constraint=False)#公司
    rank=models.IntegerField()#名次
    shareholder=models.ForeignKey(company, on_delete=models.CASCADE,related_name='cir_shareholder_com',db_constraint=False)#股东名称
    nature=models.CharField(max_length=20,null=True,blank=True)  # 股东性质
    type=models.CharField(max_length=20,null=True,blank=True)  # 股份类型
    sharenum=models.CharField(max_length=20,null=True,blank=True)  # 持股数
    percentage_share=models.CharField(max_length=20,null=True,blank=True)  # 占流通股比例
    change=models.CharField(max_length=20,null=True,blank=True)  # 增减股
    percentage_change=models.CharField(max_length=20,null=True,blank=True)  #变动比例
    date=models.DateField()#日期

    class Meta:
        db_table='cir_shareholder'


#公司关系表
class com_relation(models.Model):
    company_one = models.ForeignKey(company,on_delete=models.CASCADE,related_name='company_one', db_constraint=False)#公司1
    company_two = models.ForeignKey(company, on_delete=models.CASCADE, related_name='company_two',
                                    db_constraint=False)  # 公司2
    table_name=models.CharField(max_length=20,null=True)#表名
    relation_name=models.ForeignKey(relation_info,to_field="name", on_delete=models.CASCADE, related_name='relation_name',
                                    db_constraint=False)
    gmt_date=models.DateField(null=True)#日期
    class Meta:
        db_table='com_relation'
        unique_together=('company_one','company_two','relation_name')
