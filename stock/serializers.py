from django.contrib.auth.models import User, Group #引入django身份验证机制User模块和Group模块
from rest_framework import serializers #引入rest framework的serializers

class UserSerializer(serializers.HyperlinkedModelSerializer): #继承超链接模型解析器
    class Meta:
        model = User #使用User model
        fields = ('url', 'username', 'email', 'groups') #设置字段

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group  #使用Group model
        fields = ('url', 'name')
from stock import models
class stock_info_serializer(serializers.HyperlinkedModelSerializer):
    # highlight = serializers.HyperlinkedIdentityField(view_name='stockInfo-highlight', format='html')
    class Meta:
        model = models.stock_info
        fields = ('stock_id', 'stock_name', 'theme_id', 'theme_name', 'description', )
    # def __str__(self):
    #     return '[{}] {} ({})'.format(self.stock_id, self.stock_name)
    #
    # def create(self, validated_data):
    #     # dict -->  data --> attrs  -->  validated_data
    #     # validated_data 此处其实就是views.py中的dict
    #     # validated_data 已经被验证过的数据
    #
    #     # *  对列表进行解包    *list
    #     # ** 对字典进行解包    **dict
    #     #   此处解包  将dict中的值 赋值给对象中的对应字段
    #     stock = models.stock_info.objects.create(**validated_data)
    #
    #     # create 需要将创建的对象返回
    #     return stock
    # def update(self, instance, validated_data):
    #     """
    #     Update and return an existing `Snippet` instance, given the validated data.
    #     """
    #     instance.stock_id = validated_data.get('stock_id', instance.stock_id )
    #     instance.stock_name = validated_data.get('stock_name', instance.stock_name )
    #     instance.theme_id = validated_data.get('theme_id', instance.theme_id)
    #     instance.theme_name = validated_data.get('theme_name', instance.theme_name)
    #     instance.description = validated_data.get('description', instance.description)
    #     instance.save()
    #     return instance

class SelectionSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username') #只读
    class Meta:
        model = models.Selection
        fields = ('id', 'stock_code', 'gmt_create', 'owner')

#用于注册的时候返回json数据
class CustomerRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Customer
        fields = ('id', 'username','password', 'sex','gmt_create','user_phone')
#返回用户的选股列表
class CustomerSerializer(serializers.ModelSerializer):
    selection_set = models.Customer.objects.filter(username__exact='Customer.username')
    class Meta:
        model = models.Customer
        fields = ('id', 'username', 'selection_set')

#返回股评统计
class StatisticsSerializer(serializers.ModelSerializer):
    # stock_name = models.stock_info.objects.get(stock_id='stock_code')
    class Meta:
        model = models.propensity_statistics
        fields = ('stock_code', 'date', 'total_posts','bullish_num','bearish_num','neutral_num','storage_location','description')