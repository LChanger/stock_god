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
from stock_info import models
class stock_info_serializer(serializers.Serializer):
    stock_id=serializers.IntegerField(required=True,label='id')
    stock_name = serializers.CharField(required=True,max_length=20,label='股票名')
    theme_id= serializers.CharField(required=False,max_length=20)
    theme_name = serializers.CharField(required=False,max_length=20)
    description = serializers.CharField(required=False)

    def __str__(self):
        return '[{}] {} ({})'.format(self.stock_id, self.stock_name)

    def create(self, validated_data):
        # dict -->  data --> attrs  -->  validated_data
        # validated_data 此处其实就是views.py中的dict
        # validated_data 已经被验证过的数据

        # *  对列表进行解包    *list
        # ** 对字典进行解包    **dict
        #   此处解包  将dict中的值 赋值给对象中的对应字段
        stock = models.stock_info.objects.create(**validated_data)

        # create 需要将创建的对象返回
        return stock
    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        instance.stock_id = validated_data.get('stock_id', instance.stock_id )
        instance.stock_name = validated_data.get('stock_name', instance.stock_name )
        instance.theme_id = validated_data.get('theme_id', instance.theme_id)
        instance.theme_name = validated_data.get('theme_name', instance.theme_name)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance