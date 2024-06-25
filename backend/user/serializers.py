from rest_framework import serializers
from managers.models import venues
from user.models import Customusers



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


