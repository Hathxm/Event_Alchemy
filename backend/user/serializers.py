from rest_framework import serializers
from managers.models import venues
from .models import Customusers,Booking
from managers.serializers import ManagerSerializer
from vendors.serializers import VendorserviceSerializer
from superadmin.serializers import EventSerializer
from chat.models import ChatMessage, ChatRoom



class VenueSerializer(serializers.ModelSerializer):
    event_type_name = serializers.ReadOnlyField(source='event_type.name')  # Access the name field of the related event
    location_name = serializers.ReadOnlyField(source='location.name')  # Access the name field of the related event


    class Meta:
        model = venues
        fields = ['id', 'image1', 'image2','image3','venue_name', 'price_per_hour', 'accomodation', 'event_type_name','description','location_name','event_type','location']




class CustomuserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customusers
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'profile_pic', 'is_superuser','date_joined']



class BookingSerializer(serializers.ModelSerializer):
    customer = CustomuserSerializer(read_only=True)
    venue = VenueSerializer(read_only=True)
    services = VendorserviceSerializer(many=True, read_only=True)
    manager = ManagerSerializer(read_only=True)
    event_name = serializers.ReadOnlyField(source='event_type.name')
    customer_id = serializers.ReadOnlyField(source='customer.id')
    customer_name =  serializers.ReadOnlyField(source='customer.username')
    manager_name = serializers.ReadOnlyField(source='manager.username')
   

    class Meta:
        model = Booking
        fields = ['id', 'customer', 'venue', 'date', 'start_time', 'end_time', 'Total', 'services', 'manager','event_name','customer_id','customer_name','manager_name']
        read_only_fields = ['customer', 'venue', 'services', 'manager','event_name','customer_id']    

class ChatRoomSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.username')
    manager_name = serializers.ReadOnlyField(source='manager.username')
    user_id = serializers.ReadOnlyField(source='user.id')
    manager_id = serializers.ReadOnlyField(source='manager.id')
    user_profile_pic = serializers.SerializerMethodField()


    class Meta:
        model = ChatRoom
        fields = ['user','manager','manager_name','user_name','user_id','manager_id','user_profile_pic']

    def get_user_profile_pic(self, obj):
        return obj.user.profile_pic.url if obj.user.profile_pic else None


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = '__all__'
        