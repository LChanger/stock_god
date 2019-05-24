from django.shortcuts import render
from rest_framework import viewsets
from company import models
from company.serializers import industry_serializer,company_serializer,relation_info_serializer,\
    block_trade_serializer,com_relation_serializer,merge_reorganization_serializer,major_contract_serializer,option_invest_serializer,\
    related_transaction_serializer,person_serializer,com_per_serializer,cir_shareholder_serializer
from rest_framework import generics,request,status
from rest_framework.response import Response
from django.db import transaction#原子操作
from rest_framework.views import APIView
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

from django.db.models import Q
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
            return Response("company_one not exsit", status=status.HTTP_400_BAD_REQUEST)
        try:
            com2 = models.company.objects.get(com_name=data["com_two"])
        except Exception as e:
            return Response("company_two not exsit", status=status.HTTP_400_BAD_REQUEST)
        try:
            q = Q(company_one=com1.id,company_two=com2.id) | Q(company_one=com2.id,company_two=com1.id)  # or条件
            rel = models.com_relation.objects.filter(q)
        except Exception as e:
            return Response("relation is not exsit", status=status.HTTP_400_BAD_REQUEST)
        serializer=com_relation_serializer(rel,many=True)
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
            serializer = industry_serializer(data=data)
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
#按任意字段查询公司信息
class CompanyQuery(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.company.objects.all()
    serializer_class = company_serializer
    def post(self, request,*args, **kwargs):
        data = request.data
        try:
            res= self.queryset.get(*args, **data)
        except self.queryset.model.DoesNotExist:
            return Response("company is not exsit", status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(res)
        return Response(serializer.data)

#todo 按任意字段查询信息 父类
class DataQuery(generics.GenericAPIView):
    #返回公司
    def QueryGet(self,*args, data):
        try:
            return self.queryset.get(*args, **data)
        except self.queryset.model.DoesNotExist:
            return Response("company is not exsit", status=status.HTTP_404_NOT_FOUND)
    #返回多条信息
    def QueryFilter(self,*args, data):
        try:
            res= self.queryset.filter(*args, **data)
        except self.queryset.model.DoesNotExist:
            return Response("company is not exsit", status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(res,many=True)
        return Response(serializer.data)
#按公司名称查询
# class CompanyQuery(APIView):
#     def post(self, request,format=None):
#         data=request.data
#         try:
#             com = models.company.objects.get(com_name=data["name"])
#         except Exception as e:
#             return Response("company is not exsit", status=status.HTTP_404_NOT_FOUND)
#         serializer=company_serializer(instance=com)
#         return Response(serializer.data, status=status.HTTP_200_OK)

#规则类
class Rules():
    # 如果不存在该公司，先在company表中创建该公司,如果存在则直接取出
    def check_com(self,com):
        try:
            comp = models.company.objects.get(com_name=com)
        except Exception as e:
            comp = None
        if comp == None:
            com_data = {}
            com_data["com_name"] = com
            comserializer = company_serializer(data=com_data)
            if comserializer.is_valid(raise_exception=True):
                comserializer.save()
                comp = models.company.objects.get(com_name=com)
        return comp
    # 如果不存在该人员，先在company_person表中创建该人员,如果存在则直接取出
    def check_per(self,per):
        try:
            person = models.person.objects.get(name=per)
        except Exception as e:
            person = None
        if person == None:
            person_data = {}
            person_data["name"] = per
            perserializer = person_serializer(data=person_data)
            if perserializer.is_valid(raise_exception=True):
                perserializer.save()
                person = models.person.objects.get(name=per)
        return person
    # 如果不存在该类关系，先在relation_info表中创建该关系,如果存在则直接取出
    def check_relation(self,rel):
        try:
            rela = models.relation_info.objects.get(name=rel)
        except Exception as e:
            rela = None
        if rela == None:
            rela_data = {}
            rela_data["name"] = rel
            relserializer = relation_info_serializer(data=rela_data)
            if relserializer.is_valid(raise_exception=True):
                relserializer.save()
                rela = models.relation_info.objects.get(name=rel)
        return rela
    # 向关系表中插入数据
    def inesert_relation(self,com_one_id,company_two_id,info_name):
        rel_data = {}
        rel_data["company_one"] = com_one_id
        rel_data["company_two"] = company_two_id
        relation_info = self.check_relation(info_name)
        rel_data["relation_name"] = relation_info.name
        rel_data["table_name"] = relation_info.table_name
        relation_serializer = com_relation_serializer(data=rel_data)
        if relation_serializer.is_valid(raise_exception=True):
            relation_serializer.save()
        else:
            return relation_serializer.errors,False
        return relation_serializer.data,True
    # 向公司人员表中插入数据
    def inesert_comper(self,com_id,per_id,info_name,app_time=None):
        rel_data = {}
        rel_data["company"] = com_id
        rel_data["person"] = per_id
        rel_data["post"] = info_name
        rel_data["app_time"] =app_time
        relation_serializer = com_per_serializer(data=rel_data)
        if relation_serializer.is_valid(raise_exception=True):
            relation_serializer.save()
        else:
            return relation_serializer.errors,False
        return relation_serializer.data,True

#大宗交易的list和post
class BlockTradeList(generics.ListCreateAPIView):
    queryset = models.block_trade.objects.all()
    serializer_class = block_trade_serializer
    def post(self, request, *args, **kwargs):
        data = request.data
        rule=Rules()
        # 如果不存在买方公司，先在company表中创建买方公司
        buyer=rule.check_com(data["buyer"])
        data['buyer'] = buyer.id
        data['buyer_name'] = buyer.com_name
        #如果不存在卖方公司，先在company表中创建卖方公司
        seller = rule.check_com(data["seller"])
        data['seller'] = seller.id
        data['seller_name'] = seller.com_name
        try:
            company_main = models.company.objects.get(com_name=data["company_main"])
            data["company_main"]=company_main.id
        except Exception as e:
            return Response("company_main not exsit", status=status.HTTP_400_BAD_REQUEST)
        serializer = block_trade_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            #向关系表中插入数据
            res,OK=rule.inesert_relation(buyer.id,seller.id,"大宗交易")
            if OK:
                serializer.save()
                return Response(res, status=status.HTTP_200_OK)
            return Response(res, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#按公司名称查询大宗交易信息
class BlockTradeQuery(generics.ListCreateAPIView):
    serializer_class = block_trade_serializer
    def post(self, request,*args, **kwargs):
        data = request.data
        try:
            com = models.company.objects.get(com_name=data["name"])
        except Exception as e:
            return Response("company is not exsit", status=status.HTTP_404_NOT_FOUND)
        main_com=com.trade_company.all()
        trade_buyer_com = com.trade_buyer.all()
        trade_seller_com = com.trade_seller.all()
        self.queryset =main_com|trade_buyer_com|trade_seller_com
        return self.get(request, *args, **kwargs)

#并购重组的list和post
class MergeReList(generics.ListCreateAPIView):
    queryset = models.merge_reorganization.objects.all()
    serializer_class = merge_reorganization_serializer
    def post(self, request, *args, **kwargs):
        data = request.data
        rule=Rules()
        # 如果不存在买方公司，先在company表中创建买方公司
        buyer=rule.check_com(data["buyer"])
        data['buyer'] = buyer.id
        data['buyer_name'] = buyer.com_name
        #如果不存在卖方公司，先在company表中创建卖方公司
        seller = rule.check_com(data["seller"])
        data['seller'] = seller.id
        data['seller_name'] = seller.com_name
        # 如果不存在交易标的，先在company表中创建交易标的公司
        target = rule.check_com(data["transaction_target"])
        data['transaction_target'] = target.id
        data['target_name'] = target.com_name
        company_main = rule.check_com(data["company_main"])
        data["company_main"]=company_main.id
        serializer = merge_reorganization_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            #向关系表中插入数据
            res,OK1=rule.inesert_relation(buyer.id,seller.id,"并购重组")#卖方买方关系
            res, OK2 = rule.inesert_relation(target.id, seller.id, "并购重组")#交易标的与买方
            res, OK3 = rule.inesert_relation(target.id, buyer.id, "并购重组")#交易标的与卖方
            if OK1 and OK2 and OK3:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(res, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#按公司名称查询并购重组信息
class MergeReQuery(generics.ListCreateAPIView):
    serializer_class = merge_reorganization_serializer
    def post(self, request,*args, **kwargs):
        data = request.data
        try:
            com = models.company.objects.get(com_name=data["name"])
        except Exception as e:
            return Response("company is not exsit", status=status.HTTP_404_NOT_FOUND)
        self.queryset=com.merge_company.all()
        return self.get(request, *args, **kwargs)

#重大合同的list和post
class MajorContractList(generics.ListCreateAPIView):
    queryset = models.major_contract.objects.all()
    serializer_class = major_contract_serializer
    def post(self, request, *args, **kwargs):
        data = request.data
        rule=Rules()
        # 如果不存在签署公司，先在company表中创建签署主体公司
        signing_body=rule.check_com(data["signing_body_name"])
        data['signing_body'] = signing_body.id
        #如果不存在其他签署方公司，先在company表中创建该公司
        signing_others = rule.check_com(data["signing_others_name"])
        data['signing_others'] = signing_others.id
        # data['seller_name'] = signing_others.com_name
        body_relation=rule.check_relation(data["body_relation_name"])
        data['body_relation'] = body_relation.id
        #如果不存在该关系则先创建该关系
        others_relation = rule.check_relation(data["others_relation_name"])
        data['others_relation'] = others_relation.id
        #如果不存在该公司则先创建该公司
        company_main = rule.check_com(data["company_main"])
        data["company_main"]=company_main.id
        serializer = major_contract_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            #向关系表中插入数据
            res,OK1=rule.inesert_relation(signing_body.id,company_main.id,data["body_relation_name"])##签署主体与上市公司的关系
            res, OK2 = rule.inesert_relation(company_main.id, signing_others.id,data["others_relation_name"])#其他签署方与上市公司的关系
            res, OK3 = rule.inesert_relation(company_main.id, signing_others.id,"重大合同")#交易标的与卖方
            if OK1 and OK2 and OK3:
                serializer.save()
                return Response(res, status=status.HTTP_200_OK)
            return Response(res, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#长期期权投资的list和post
class OptionInvestList(generics.ListCreateAPIView):
    queryset = models.option_invest.objects.all()
    serializer_class = option_invest_serializer
    def post(self, request, *args, **kwargs):
        data = request.data
        rule=Rules()
        # 如果不存在投资公司，先在company表中创建该公司
        invest_com=rule.check_com(data["invest_com"])
        data['invest_com'] = invest_com.id
        #如果不存在该公司则先创建该公司
        company_main = rule.check_com(data["company_main"])
        data["company_main"]=company_main.id
        serializer = option_invest_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            #向关系表中插入数据
            res, OK = rule.inesert_relation(company_main.id, invest_com.id,"长期期权投资")#交易标的与卖方
            if OK:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(res, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#关联交易的list和post
class RelatedTransactionList(generics.ListCreateAPIView):
    queryset = models.related_transaction.objects.all()
    serializer_class = related_transaction_serializer
    def post(self, request, *args, **kwargs):
        data = request.data
        rule=Rules()
        # 如果不存在交易公司，先在company表中创建该公司
        transaction_com=rule.check_com(data["transaction_com"])
        data['transaction_com'] = transaction_com.id
        #如果不存在该公司则先创建该公司
        company_main = rule.check_com(data["company_main"])
        data["company_main"]=company_main.id
        serializer = related_transaction_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            #向关系表中插入数据
            res, OK = rule.inesert_relation(company_main.id, transaction_com.id,"关联交易")#交易标的与卖方
            if OK:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(res, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#十大流通股东的list和post
class CirShareholderList(generics.ListCreateAPIView):
    queryset = models.related_transaction.objects.all()
    serializer_class = related_transaction_serializer
    def post(self, request, *args, **kwargs):
        data = request.data
        rule = Rules()
        #如果不存在该公司则先创建该公司
        company_main = rule.check_com(data["company_main"])
        data["company_main"]=company_main.id
        try:
            with transaction.atomic():
                if data["nature"] == '其它':
                    # 如果不存在股东公司，先在company表中创建该公司
                    shareholder_com = rule.check_com(data["shareholder"])
                    res, OK = rule.inesert_relation(company_main.id, shareholder_com.id, "十大流通股东")  #
                    if not OK: return Response(res, status=status.HTTP_400_BAD_REQUEST)
                    data["shareholder"] = shareholder_com.id
                if data["nature"] == '个人':
                    per = rule.check_per(data["shareholder"])
                    res, OK = rule.inesert_comper(company_main.id, per.id, "十大流通股东", data["date"])
                    if not OK: return Response(res, status=status.HTTP_400_BAD_REQUEST)
                    data["shareholder"]=per.id
                serializer = cir_shareholder_serializer(data=data)
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(e.args, status=status.HTTP_400_BAD_REQUEST)
#人员的list和post
class PersonList(generics.ListCreateAPIView):
    queryset = models.person.objects.all()
    serializer_class = person_serializer
    # def get(self, request, *args, **kwargs):
    #     perserializer = person_serializer(self.queryset)

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = person_serializer(data=data)
        try:
            with transaction.atomic():
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                    person = models.person.objects.get(name=data["name"])
                    rule = Rules()
                    # 如果不存在关联公司，先在company表中创建该公司
                    com = rule.check_com(data["com"])
                    t = data["app_time"].split('-')
                    y, m, d = int(t[0]), int(t[1]), int(t[2])
                    import datetime
                    Date = datetime.date(y, m, d)
                    cp = models.com_per(person=person, company=com, post=data["post"], app_time=Date)
                    cp.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(e.args, status=status.HTTP_400_BAD_REQUEST)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#人员与公司关系的list和post
class PersonComList(generics.ListCreateAPIView):
    queryset = models.com_per.objects.all()
    serializer_class = com_per_serializer
    # def get(self, request, *args, **kwargs):
    #     perserializer = person_serializer(self.queryset)

    # def post(self, request, *args, **kwargs):
    #     data = request.data
    #     serializer = person_serializer(data=data)

#人员与公司关系的list和post
from py2neo import Graph,NodeMatcher,Node,Relationship
class ComsList(APIView):
    def __init__(self):
        self.conn = Graph("http://localhost:7474", username="neo4j", password="123456")
    def importToNeo4j(self):
        #创建公司结点
        companys = models.company.objects.all()
        for i, c in enumerate(companys):
            com = Node('Company', company_id=c.id, company_name=c.com_name, stock_code_A=c.stock_code_A)
            self.conn.create(com)
        #创建公司与公司之间关系
        rel=models.com_relation.objects.all()
        for i, r in enumerate(rel):
            com1 = self.conn.nodes.match('Company', company_id=r.company_one_id).first()
            com2=self.conn.nodes.match('Company', company_id=r.company_two_id).first()
            rship = Relationship(com1, r.relation_name_id, com2)
            self.conn.create(rship)
        #创建人员
        persons = models.person.objects.all()
        for i, p in enumerate(persons):
            per= Node('Person',person_id=p.id, name=p.name, age=p.ages,edu=p.edu_background,introduction=p.introduction)
            self.conn.create(per)
        #创建人员与公司之间的关系
        per_com=models.com_per.objects.all()
        for i,r in enumerate(per_com):
            per = self.conn.nodes.match('Person', person_id=r.person_id).first()
            com = self.conn.nodes.match('Company', company_id=r.company_id).first()
            rship = Relationship(per, str(r.post), com,app_time=r.app_time.strftime("%Y-%m-%d"))
            self.conn.create(rship)
        return True
    def supplyNeo4j(self):
        companys=models.company.objects.all()
        for i,c in enumerate(companys):
            org = self.conn.nodes.match("Company", company_id=c.id).first()
            if org==None:
                com=Node('Company',company_id=c.id,company_name=c.com_name,stock_code_A=c.stock_code_A)
                self.conn.create(com)
                rel = models.com_relation.objects.filter(company_one=c.id)
                for r in rel:
                    org=self.conn.nodes.match("Company", company_id=r.company_two_id).first()
                    if org!=None:
                        rship = self.conn.match(nodes=[com,org], r_type=r.relation_name_id)
                        if rship==None:
                            Relationship(com,r.relation_name_id,org)
                            self.conn.create(rship)
                #查找该公司的关系
                rel = models.com_relation.objects.filter(company_two=c.id)
                for r in rel:
                    org=self.conn.nodes.match("Company", company_id=r.company_one_id).first()
                    if org!=None:
                        #若neo4j中不存在该关系则生成
                        rship = self.conn.match(nodes=[com, org], r_type=r.relation_name_id)
                        if rship==None:
                            Relationship(com,r.relation_name_id,org)
                            self.conn.create(rship)
        #扫描人员列表，查找新插入的人员信息
        persons = models.person.objects.all()
        for i, p in enumerate(persons):
            org = self.conn.nodes.match("Person", person_id=p.id).first()
            if org == None:
                per = Node('Person', person_id=p.id, name=p.name, age=p.ages, edu=p.edu_background,
                           introduction=p.introduction)
                self.conn.create(per)
                rel = models.com_per.objects.filter(person=p.id)
                for r in rel:
                    org = self.conn.nodes.match("Company", company_id=r.company_id).first()
                    if org != None:
                        rship=Relationship(per, r.post,org,app_time=r.app_time.strftime("%Y-%m-%d"))
                        self.conn.create(rship)

        #     items.append(data)
        # statement_c = """MERGE (node1:Company {person_name:{person_name}})
        #                  MERGE (node2:Company {company_name:{company_name}})
        #                  MERGE (node1)<-[:Query {visit_time: {visit_time}}]-(node2)"""
        # statement_c = """CREATE (node1:Company {person_name:{person_name}}))"""
        # tx=Graph().begin()

    def post(self,request,format=None):
        graph = Graph()
        matcher = NodeMatcher(graph)
        # self.importToNeo4j()
        self.supplyNeo4j()
        res=matcher.match('Company').where("_.company_name='湖北司马彦文化科技有限公司'")
        return Response(res,status=status.HTTP_200_OK)