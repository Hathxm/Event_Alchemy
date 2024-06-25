from rest_framework import serializers
from .models import vendorservices,Vendors

class VendorserviceSerializer(serializers.ModelSerializer):
    service_name = serializers.ReadOnlyField(source='service_type.service_name', default=None)

    class Meta:
        model = vendorservices
        fields = ['id','vendor','service_type','price','description','service_name','is_active']

class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendors 
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'profile_pic', 'is_superuser','date_joined','is_vendor']


