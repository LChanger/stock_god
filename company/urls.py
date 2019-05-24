"""stock_god URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.contrib import admin
from company import views
from django.conf.urls import url, include
from rest_framework import routers, serializers, viewsets
from django.urls import path, include


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'industry', views.IndustryViewSet)
router.register(r'relation', views.RelationInfoViewSet)
router.register(r'comrelation',views.ComRelationViewSet)

# router.register(r'analysis', views.CommentAnalysis)#评论倾向性分析
# router.register(r'comment/analysis/',views.CommentAnalysis.as_view())
# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls)),
    path(r'company/', views.CompanyList.as_view()),
    path(r'company/<int:pk>/', views.CompanyDetail.as_view()),
    path(r'company/query/',views.CompanyQuery.as_view()),#按公司名称查询
    path(r'mergereorganization/', views.MergeReList.as_view()),
    path(r'blocktrade/', views.BlockTradeList.as_view()),
    path(r'blocktrade/query/', views.BlockTradeQuery.as_view()),#按公司名称查询大宗交易
    path(r'majorcontract/', views.MajorContractList.as_view()),
    path(r'optioninvest/', views.OptionInvestList.as_view()),
    path(r'relatedtransaction/', views.RelatedTransactionList.as_view()),
    path(r'shareholder/',views.CirShareholderList.as_view()),#十大流通股东
    path(r'person/', views.PersonList.as_view()),
    path(r'personcom/', views.PersonComList.as_view()),
    path(r'comneo/',views.ComsList.as_view()),#求任意两公司之间的关系neo4j 操作
]


