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

# Routers provide an easy way of automatically determining the URL conf.
from django.urls import path
from stock import views
from rest_framework.urlpatterns import format_suffix_patterns
urlpatterns = [
    path('stock/info/', views.StockInfoList.as_view()),
    path('stock/info/<str:pk>/', views.StockInfoDetail.as_view()),#detail about stock_info
    path('', views.api_root),
    path('stock/info/<int:pk>/highlight/', views.StockHighlight.as_view(),name='stockInfo-highlight'),
    # url(r'^statistics/union/$',views.StatisticsDetail.as_view())
    path('comment/analysis/', views.CommentAnalysis.as_view()),#评论倾向分析
]
